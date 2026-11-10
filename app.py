"""
app.py
AI Powered Resume Screening and Ranking System
Flask Web Application & API Server
"""

import os
import csv
import io
import json
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, Response, send_from_directory
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from config import Config
from database import (
    init_db, get_user_by_email, get_user_by_id, create_user,
    get_all_jobs, get_job_by_id, create_job, delete_job,
    save_resume, save_screening, get_screenings_for_job,
    get_screening_by_id, update_screening_status, get_dashboard_stats
)
from models.parser import parse_resume
from models.extractor import extract_full_profile
from models.ranker import rank_candidate

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database and folders exist
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this portal.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to inject user into templates
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return dict(current_user=user)

# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", "success")
            
            # Direct candidate to candidate portal, recruiter to dashboard
            if user['role'] == 'candidate':
                return redirect(url_for('candidate_portal'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'recruiter')

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return render_template('register.html')

        user_id = create_user(name, email, password, role)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_role'] = role
            flash("Account registered successfully! Welcome aboard.", "success")
            if role == 'candidate':
                return redirect(url_for('candidate_portal'))
            return redirect(url_for('dashboard'))
        else:
            flash("An account with that email already exists. Please log in.", "danger")

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------------
# DASHBOARD ROUTE
# -------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    jobs = get_all_jobs()
    return render_template('dashboard.html', stats=stats, jobs=jobs)

# -------------------------------------------------------------
# JOB MANAGEMENT ROUTES
# -------------------------------------------------------------

@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        min_experience = float(request.form.get('min_experience', 0))
        min_education = request.form.get('min_education', 'B.Tech')
        description = request.form.get('description', '').strip()
        skills_raw = request.form.get('skills', '').strip()

        # Parse comma-separated skills
        skills_list = [s.strip().lower() for s in skills_raw.split(',') if s.strip()]

        # Weights
        try:
            skill_w = float(request.form.get('skill_weight', 45)) / 100.0
            sem_w = float(request.form.get('semantic_weight', 25)) / 100.0
            exp_w = float(request.form.get('experience_weight', 15)) / 100.0
            edu_w = float(request.form.get('education_weight', 15)) / 100.0
        except ValueError:
            skill_w, sem_w, exp_w, edu_w = 0.45, 0.25, 0.15, 0.15

        weights = {
            "skill_weight": skill_w,
            "semantic_weight": sem_w,
            "experience_weight": exp_w,
            "education_weight": edu_w
        }

        job_id = create_job(
            title, department, location, job_type, min_experience,
            min_education, description, skills_list, weights, session.get('user_id', 1)
        )
        flash(f"Job posting '{title}' created successfully!", "success")
        return redirect(url_for('jobs'))

    all_jobs = get_all_jobs()
    return render_template('jobs.html', jobs=all_jobs)

@app.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job_route(job_id):
    delete_job(job_id)
    flash("Job posting removed successfully.", "info")
    return redirect(url_for('jobs'))

# -------------------------------------------------------------
# SCREENING & RANKING WORKBENCH
# -------------------------------------------------------------

@app.route('/screen', methods=['GET', 'POST'])
@login_required
def screen():
    jobs = get_all_jobs()
    selected_job_id = request.args.get('job_id', type=int)

    if not selected_job_id and jobs:
        selected_job_id = jobs[0]['id']

    current_job = get_job_by_id(selected_job_id) if selected_job_id else None

    # Handle multi-file resume uploads
    if request.method == 'POST':
        if not current_job:
            flash("Please select a target job opening first.", "warning")
            return redirect(url_for('screen'))

        files = request.files.getlist('resumes')
        if not files or files[0].filename == '':
            flash("Please select at least one resume file to upload.", "warning")
            return redirect(url_for('screen', job_id=selected_job_id))

        processed_count = 0
        error_count = 0

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)

                # 1. Parse resume text
                parsed = parse_resume(save_path)
                if not parsed['success']:
                    error_count += 1
                    continue

                # 2. Extract entities (Name, Email, Skills, Experience, Education)
                profile = extract_full_profile(parsed['text'], filename)

                # 3. Store resume
                resume_id = save_resume(filename, save_path, profile, session.get('user_id'))

                # 4. Run AI ranking model against the target job
                weights = {
                    "skill_weight": current_job.get("skill_weight", 0.45),
                    "semantic_weight": current_job.get("semantic_weight", 0.25),
                    "experience_weight": current_job.get("experience_weight", 0.15),
                    "education_weight": current_job.get("education_weight", 0.15)
                }
                ranking_result = rank_candidate(profile, current_job, weights)

                # 5. Persist screening result
                save_screening(selected_job_id, resume_id, ranking_result)
                processed_count += 1
            else:
                error_count += 1

        if processed_count > 0:
            flash(f"Successfully screened and ranked {processed_count} candidate resume(s)!", "success")
        if error_count > 0:
            flash(f"{error_count} file(s) were skipped due to unsupported formats or extraction errors.", "warning")

        return redirect(url_for('screen', job_id=selected_job_id))

    # Fetch ranked leaderboard for selected job
    ranked_candidates = get_screenings_for_job(selected_job_id) if selected_job_id else []

    return render_template(
        'screen.html',
        jobs=jobs,
        current_job=current_job,
        selected_job_id=selected_job_id,
        ranked_candidates=ranked_candidates
    )

@app.route('/screen/load-samples/<int:job_id>', methods=['POST'])
@login_required
def load_sample_resumes(job_id):
    """
    1-Click Instant Demo: Ingests all pre-packaged sample resumes into the active job!
    """
    current_job = get_job_by_id(job_id)
    if not current_job:
        flash("Job not found.", "danger")
        return redirect(url_for('screen'))

    sample_dir = app.config['SAMPLE_FOLDER']
    if not os.path.exists(sample_dir):
        flash("Sample resumes directory not found.", "warning")
        return redirect(url_for('screen', job_id=job_id))

    # Prefer PDF or DOCX samples
    files = [f for f in os.listdir(sample_dir) if f.endswith(('.pdf', '.docx'))]
    # Unique base names to avoid duplicates if both pdf and docx exist
    seen_bases = set()
    selected_files = []
    for f in sorted(files):
        base = os.path.splitext(f)[0]
        if base not in seen_bases:
            seen_bases.add(base)
            selected_files.append(f)

    loaded = 0
    weights = {
        "skill_weight": current_job.get("skill_weight", 0.45),
        "semantic_weight": current_job.get("semantic_weight", 0.25),
        "experience_weight": current_job.get("experience_weight", 0.15),
        "education_weight": current_job.get("education_weight", 0.15)
    }

    for f in selected_files:
        f_path = os.path.join(sample_dir, f)
        parsed = parse_resume(f_path)
        if parsed['success']:
            profile = extract_full_profile(parsed['text'], f)
            resume_id = save_resume(f, f_path, profile, session.get('user_id'))
            ranking = rank_candidate(profile, current_job, weights)
            save_screening(job_id, resume_id, ranking)
            loaded += 1

    flash(f"Loaded and screened {loaded} sample candidate resumes! Review the ranked leaderboard below.", "success")
    return redirect(url_for('screen', job_id=job_id))

# -------------------------------------------------------------
# CANDIDATE PROFILE & DETAIL REPORT
# -------------------------------------------------------------

@app.route('/candidate/<int:screening_id>')
@login_required
def candidate_detail(screening_id):
    screening = get_screening_by_id(screening_id)
    if not screening:
        flash("Screening record not found.", "warning")
        return redirect(url_for('screen'))

    return render_template('candidate_view.html', item=screening)

@app.route('/candidate/<int:screening_id>/status', methods=['POST'])
@login_required
def update_status(screening_id):
    new_status = request.form.get('status')
    if new_status in ['Screened', 'Shortlisted', 'Interview', 'Rejected']:
        update_screening_status(screening_id, new_status)
        flash(f"Candidate status updated to '{new_status}'.", "info")
    return redirect(url_for('candidate_detail', screening_id=screening_id))

@app.route('/job/<int:job_id>/export-csv')
@login_required
def export_csv(job_id):
    job = get_job_by_id(job_id)
    screenings = get_screenings_for_job(job_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Rank", "Candidate Name", "Email", "Phone", "Education",
        "Experience (Yrs)", "Overall Score (%)", "Skill Match (%)",
        "Semantic Score (%)", "Verdict", "Status", "Matched Skills", "Missing Skills"
    ])

    for rank, s in enumerate(screenings, start=1):
        writer.writerow([
            rank,
            s['candidate_name'],
            s['email'],
            s['phone'],
            s['education'],
            s['experience_years'],
            s['overall_score'],
            s['skill_score'],
            s['semantic_score'],
            s['verdict'],
            s['status'],
            ", ".join(s['matched_skills']),
            ", ".join(s['missing_skills'])
        ])

    csv_data = output.getvalue()
    filename = f"Screening_Report_Job_{job_id}_{job['title'].replace(' ', '_')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# -------------------------------------------------------------
# CANDIDATE SELF-SERVICE PORTAL (APPLICANT VIEW)
# -------------------------------------------------------------

@app.route('/portal', methods=['GET', 'POST'])
def candidate_portal():
    jobs = get_all_jobs()
    analysis = None
    selected_job = None

    if request.method == 'POST':
        job_id = request.form.get('job_id', type=int)
        selected_job = get_job_by_id(job_id) if job_id else None

        file = request.files.get('resume')
        if not file or file.filename == '':
            flash("Please choose a resume file (.pdf, .docx, or .txt).", "warning")
            return render_template('candidate_portal.html', jobs=jobs, analysis=None)

        if not allowed_file(file.filename):
            flash("File format not supported. Please upload a PDF, DOCX, or TXT file.", "danger")
            return render_template('candidate_portal.html', jobs=jobs, analysis=None)

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        parsed = parse_resume(save_path)
        if not parsed['success']:
            flash(f"Error parsing resume: {parsed['error']}", "danger")
            return render_template('candidate_portal.html', jobs=jobs, analysis=None)

        profile = extract_full_profile(parsed['text'], filename)

        if selected_job:
            weights = {
                "skill_weight": selected_job.get("skill_weight", 0.45),
                "semantic_weight": selected_job.get("semantic_weight", 0.25),
                "experience_weight": selected_job.get("experience_weight", 0.15),
                "education_weight": selected_job.get("education_weight", 0.15)
            }
            ranking = rank_candidate(profile, selected_job, weights)
            # Save into DB as applicant submission
            user_id = session.get('user_id')
            resume_id = save_resume(filename, save_path, profile, user_id)
            screening_id = save_screening(job_id, resume_id, ranking)

            analysis = {
                "profile": profile,
                "ranking": ranking,
                "job": selected_job,
                "screening_id": screening_id
            }
            flash("Your resume was parsed and scored against the job criteria!", "success")
        else:
            # General ATS check without job
            analysis = {
                "profile": profile,
                "ranking": None,
                "job": None
            }
            flash("General ATS resume review completed!", "info")

    return render_template('candidate_portal.html', jobs=jobs, analysis=analysis, selected_job=selected_job)

# -------------------------------------------------------------
# ARCHITECTURE & VIVA PREPARATION ROUTE
# -------------------------------------------------------------

@app.route('/architecture')
def architecture():
    """
    Detailed technical documentation page explaining TF-IDF, Cosine Similarity,
    information extraction, and common viva questions for college project defense.
    """
    return render_template('architecture.html')

# -------------------------------------------------------------
# RUN SERVER
# -------------------------------------------------------------

if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)
