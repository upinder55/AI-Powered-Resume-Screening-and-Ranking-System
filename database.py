"""
database.py
SQLite database manager and data access layer.
Handles schema creation, seeding sample data, and entity CRUD operations.
"""

import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and seeds default users & sample job postings."""
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.SAMPLE_FOLDER, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'recruiter',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Jobs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        location TEXT NOT NULL,
        job_type TEXT NOT NULL,
        min_experience REAL NOT NULL DEFAULT 0,
        min_education TEXT NOT NULL DEFAULT 'B.Tech',
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL, -- JSON array
        skill_weight REAL DEFAULT 0.45,
        semantic_weight REAL DEFAULT 0.25,
        experience_weight REAL DEFAULT 0.15,
        education_weight REAL DEFAULT 0.15,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')

    # Resumes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        candidate_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        linkedin TEXT,
        github TEXT,
        education TEXT,
        experience_years REAL DEFAULT 0,
        skills TEXT, -- JSON array
        categorized_skills TEXT, -- JSON object
        raw_text TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Screenings / Applications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        resume_id INTEGER NOT NULL,
        overall_score REAL NOT NULL,
        skill_score REAL NOT NULL,
        semantic_score REAL NOT NULL,
        exp_score REAL NOT NULL,
        edu_score REAL NOT NULL,
        matched_skills TEXT, -- JSON array
        missing_skills TEXT, -- JSON array
        bonus_skills TEXT, -- JSON array
        verdict TEXT NOT NULL,
        strengths TEXT, -- JSON array
        weaknesses TEXT, -- JSON array
        recommendation TEXT,
        status TEXT DEFAULT 'Screened', -- 'Screened', 'Shortlisted', 'Interview', 'Rejected'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()

    # Seed default data if empty
    seed_default_data(conn)
    conn.close()

def seed_default_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Seed users
        recruiter_pw = generate_password_hash("admin123")
        candidate_pw = generate_password_hash("admin123")

        cursor.execute('''
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        ''', ("Sarah Jenkins (HR Lead)", "recruiter@college.edu", recruiter_pw, "recruiter"))

        cursor.execute('''
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        ''', ("Alex Rivera (Applicant)", "candidate@college.edu", candidate_pw, "candidate"))

        # Seed sample job postings
        sample_jobs = [
            (
                "AI / Machine Learning Engineer",
                "Data & AI Labs",
                "Bangalore / Hybrid",
                "Full-time",
                3.0,
                "B.Tech",
                "We are seeking an AI/ML Engineer to build predictive models, NLP pipelines, and generative AI solutions. Candidates must have strong proficiency with Python, PyTorch or TensorFlow, scikit-learn, data preprocessing, and containerization with Docker. Experience with Hugging Face transformers, REST APIs with FastAPI/Flask, and deploying models to cloud environments is highly valued.",
                json.dumps(["python", "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "scikit-learn", "docker", "fastapi", "git"]),
                0.45, 0.25, 0.15, 0.15, 1
            ),
            (
                "Full Stack Web Developer (Python + React)",
                "Product Engineering",
                "Remote / On-site",
                "Full-time",
                2.0,
                "B.Tech",
                "Looking for a versatile Full Stack Developer responsible for building robust web applications. The role involves designing clean RESTful microservices using Python (Django/Flask/FastAPI), responsive interactive frontends in React.js and TypeScript, and managing relational databases with PostgreSQL or MySQL. Familiarity with Git version control and CI/CD pipelines is required.",
                json.dumps(["python", "react", "javascript", "django", "flask", "postgresql", "rest api", "html5", "css3", "git"]),
                0.45, 0.25, 0.15, 0.15, 1
            ),
            (
                "Data Analyst & Business Intelligence",
                "Analytics & Strategy",
                "Mumbai / On-site",
                "Full-time",
                1.5,
                "B.Tech",
                "We need a meticulous Data Analyst to derive actionable business insights from structured and unstructured data. You will craft interactive dashboards in Tableau and Power BI, write complex SQL queries for data aggregation, and utilize Python (Pandas, NumPy, Matplotlib) for statistical data cleansing, ETL workflows, and reporting.",
                json.dumps(["python", "sql", "tableau", "power bi", "pandas", "numpy", "excel", "data analysis", "data visualization"]),
                0.45, 0.25, 0.15, 0.15, 1
            ),
            (
                "Cloud DevOps & Platform Engineer",
                "Infrastructure & Operations",
                "Hyderabad / Hybrid",
                "Full-time",
                3.0,
                "B.Tech",
                "Seeking an experienced DevOps Engineer to orchestrate multi-cloud infrastructure. Core responsibilities include managing Kubernetes clusters, writing Infrastructure-as-Code with Terraform, setting up automated CI/CD pipelines via Jenkins and GitHub Actions, and maintaining system security and Linux server observability.",
                json.dumps(["aws", "docker", "kubernetes", "linux", "ci/cd", "terraform", "jenkins", "git", "bash", "python"]),
                0.45, 0.25, 0.15, 0.15, 1
            )
        ]

        cursor.executemany('''
        INSERT INTO jobs (title, department, location, job_type, min_experience, min_education, description, required_skills, skill_weight, semantic_weight, experience_weight, education_weight, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_jobs)

        conn.commit()

# --- Auth Helpers ---
def create_user(name, email, password, role="recruiter"):
    conn = get_db_connection()
    try:
        pw_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       (name, email.strip().lower(), pw_hash, role))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

# --- Job Helpers ---
def get_all_jobs():
    conn = get_db_connection()
    jobs = conn.execute('''
    SELECT j.*, COUNT(s.id) as applicant_count, AVG(s.overall_score) as avg_score
    FROM jobs j
    LEFT JOIN screenings s ON j.id = s.job_id
    GROUP BY j.id
    ORDER BY j.created_at DESC
    ''').fetchall()
    conn.close()
    
    result = []
    for j in jobs:
        d = dict(j)
        d['required_skills'] = json.loads(d['required_skills']) if d['required_skills'] else []
        d['avg_score'] = round(d['avg_score'], 1) if d['avg_score'] is not None else 0.0
        result.append(d)
    return result

def get_job_by_id(job_id):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if job:
        d = dict(job)
        d['required_skills'] = json.loads(d['required_skills']) if d['required_skills'] else []
        return d
    return None

def create_job(title, department, location, job_type, min_exp, min_edu, desc, skills_list, weights=None, created_by=1):
    w = weights or {"skill_weight": 0.45, "semantic_weight": 0.25, "experience_weight": 0.15, "education_weight": 0.15}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO jobs (title, department, location, job_type, min_experience, min_education, description, required_skills, skill_weight, semantic_weight, experience_weight, education_weight, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        title, department, location, job_type, float(min_exp), min_edu, desc,
        json.dumps(skills_list),
        float(w.get("skill_weight", 0.45)),
        float(w.get("semantic_weight", 0.25)),
        float(w.get("experience_weight", 0.15)),
        float(w.get("education_weight", 0.15)),
        created_by
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def delete_job(job_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

# --- Resume & Screening Helpers ---
def save_resume(filename, file_path, profile, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO resumes (user_id, filename, file_path, candidate_name, email, phone, linkedin, github, education, experience_years, skills, categorized_skills, raw_text)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        filename,
        file_path,
        profile.get("name", "Candidate"),
        profile.get("email", ""),
        profile.get("phone", ""),
        profile.get("linkedin", ""),
        profile.get("github", ""),
        profile.get("education", "Not specified"),
        float(profile.get("experience_years", 0)),
        json.dumps(profile.get("skills", [])),
        json.dumps(profile.get("categorized_skills", {})),
        profile.get("raw_text", "")
    ))
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id

def save_screening(job_id, resume_id, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO screenings (
        job_id, resume_id, overall_score, skill_score, semantic_score, exp_score, edu_score,
        matched_skills, missing_skills, bonus_skills, verdict, strengths, weaknesses, recommendation, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id,
        resume_id,
        result.get("overall_score", 0),
        result.get("skill_score", 0),
        result.get("semantic_score", 0),
        result.get("exp_score", 0),
        result.get("edu_score", 0),
        json.dumps(result.get("matched_skills", [])),
        json.dumps(result.get("missing_skills", [])),
        json.dumps(result.get("bonus_skills", [])),
        result.get("verdict", "Under Review"),
        json.dumps(result.get("strengths", [])),
        json.dumps(result.get("weaknesses", [])),
        result.get("recommendation", ""),
        "Shortlisted" if result.get("overall_score", 0) >= 70 else "Screened"
    ))
    conn.commit()
    screening_id = cursor.lastrowid
    conn.close()
    return screening_id

def get_screenings_for_job(job_id):
    conn = get_db_connection()
    query = '''
    SELECT s.*, r.filename, r.candidate_name, r.email, r.phone, r.education, r.experience_years
    FROM screenings s
    JOIN resumes r ON s.resume_id = r.id
    WHERE s.job_id = ?
    ORDER BY s.overall_score DESC, s.created_at DESC
    '''
    rows = conn.execute(query, (job_id,)).fetchall()
    conn.close()

    results = []
    for row in rows:
        d = dict(row)
        d['matched_skills'] = json.loads(d['matched_skills']) if d['matched_skills'] else []
        d['missing_skills'] = json.loads(d['missing_skills']) if d['missing_skills'] else []
        d['bonus_skills'] = json.loads(d['bonus_skills']) if d['bonus_skills'] else []
        d['strengths'] = json.loads(d['strengths']) if d['strengths'] else []
        d['weaknesses'] = json.loads(d['weaknesses']) if d['weaknesses'] else []
        results.append(d)
    return results

def get_screening_by_id(screening_id):
    conn = get_db_connection()
    query = '''
    SELECT s.*, r.filename, r.candidate_name, r.email, r.phone, r.linkedin, r.github,
           r.education, r.experience_years, r.skills as candidate_skills, r.categorized_skills, r.raw_text,
           j.title as job_title, j.department, j.location, j.min_experience, j.min_education, j.required_skills as job_skills
    FROM screenings s
    JOIN resumes r ON s.resume_id = r.id
    JOIN jobs j ON s.job_id = j.id
    WHERE s.id = ?
    '''
    row = conn.execute(query, (screening_id,)).fetchone()
    conn.close()

    if not row:
        return None

    d = dict(row)
    d['matched_skills'] = json.loads(d['matched_skills']) if d['matched_skills'] else []
    d['missing_skills'] = json.loads(d['missing_skills']) if d['missing_skills'] else []
    d['bonus_skills'] = json.loads(d['bonus_skills']) if d['bonus_skills'] else []
    d['strengths'] = json.loads(d['strengths']) if d['strengths'] else []
    d['weaknesses'] = json.loads(d['weaknesses']) if d['weaknesses'] else []
    d['candidate_skills'] = json.loads(d['candidate_skills']) if d['candidate_skills'] else []
    d['categorized_skills'] = json.loads(d['categorized_skills']) if d['categorized_skills'] else {}
    d['job_skills'] = json.loads(d['job_skills']) if d['job_skills'] else []
    return d

def update_screening_status(screening_id, new_status):
    conn = get_db_connection()
    conn.execute("UPDATE screenings SET status = ? WHERE id = ?", (new_status, screening_id))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_db_connection()
    total_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_resumes = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
    total_screenings = conn.execute("SELECT COUNT(*) FROM screenings").fetchone()[0]
    shortlisted = conn.execute("SELECT COUNT(*) FROM screenings WHERE overall_score >= 70").fetchone()[0]
    avg_score_row = conn.execute("SELECT AVG(overall_score) FROM screenings").fetchone()[0]
    avg_score = round(avg_score_row, 1) if avg_score_row else 0.0

    recent_screenings = conn.execute('''
    SELECT s.id, s.overall_score, s.verdict, s.status, s.created_at,
           r.candidate_name, r.email, j.title as job_title
    FROM screenings s
    JOIN resumes r ON s.resume_id = r.id
    JOIN jobs j ON s.job_id = j.id
    ORDER BY s.created_at DESC
    LIMIT 6
    ''').fetchall()

    conn.close()

    return {
        "total_jobs": total_jobs,
        "total_resumes": total_resumes,
        "total_screenings": total_screenings,
        "shortlisted": shortlisted,
        "avg_score": avg_score,
        "recent_screenings": [dict(r) for r in recent_screenings]
    }
