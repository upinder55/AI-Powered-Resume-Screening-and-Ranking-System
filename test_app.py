"""
test_app.py
Comprehensive test suite verifying database, models, parser, ranker,
and Flask endpoints.
"""

import os
import sys

# Ensure current dir is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from database import init_db, get_all_jobs, get_user_by_email, get_screenings_for_job
from models.parser import parse_resume
from models.extractor import extract_full_profile
from models.ranker import rank_candidate

def run_tests():
    print("=========================================")
    print("Running Full System Verification Tests...")
    print("=========================================")

    # 1. DB Init
    init_db()
    jobs = get_all_jobs()
    assert len(jobs) >= 4, f"Expected at least 4 seeded jobs, found {len(jobs)}"
    print(f"✓ Database seeded successfully: {len(jobs)} active jobs found.")

    user = get_user_by_email("recruiter@college.edu")
    assert user is not None, "Recruiter user not found in DB"
    print("✓ Default users verified in database.")

    # 2. Test Parser on PDF, DOCX, TXT
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_resumes")
    pdf_sample = os.path.join(sample_dir, "Aarav_Sharma_AI_ML_Engineer.pdf")
    docx_sample = os.path.join(sample_dir, "Priya_Patel_FullStack_Developer.docx")
    txt_sample = os.path.join(sample_dir, "Rohan_Verma_Data_Analyst.txt")

    p1 = parse_resume(pdf_sample)
    assert p1['success'], f"PDF parse failed: {p1.get('error')}"
    print(f"✓ PDF Parser verified: extracted {len(p1['text'])} characters.")

    p2 = parse_resume(docx_sample)
    assert p2['success'], f"DOCX parse failed: {p2.get('error')}"
    print(f"✓ DOCX Parser verified: extracted {len(p2['text'])} characters.")

    p3 = parse_resume(txt_sample)
    assert p3['success'], f"TXT parse failed: {p3.get('error')}"
    print(f"✓ TXT Parser verified: extracted {len(p3['text'])} characters.")

    # 3. Test Extractor
    prof = extract_full_profile(p1['text'], "Aarav_Sharma_AI_ML_Engineer.pdf")
    assert prof['name'] == "Aarav Sharma", f"Extracted name: {prof['name']}"
    assert len(prof['skills']) > 5, f"Skills extracted: {prof['skills']}"
    assert prof['education'] == "B.Tech", f"Degree extracted: {prof['education']}"
    print(f"✓ Entity Extractor verified: Name={prof['name']}, Skills={len(prof['skills'])}, Degree={prof['education']}, Exp={prof['experience_years']} yrs.")

    # 4. Test Ranker
    job = jobs[0]
    rank_res = rank_candidate(prof, job)
    assert 0 <= rank_res['overall_score'] <= 100, f"Score out of bounds: {rank_res['overall_score']}"
    assert rank_res['verdict'] in ["Strong Hire", "Shortlisted", "Under Review", "Not Recommended"]
    print(f"✓ AI Ranker verified: Composite Score={rank_res['overall_score']}%, Verdict={rank_res['verdict']}.")

    # 5. Test Flask Client Routes
    client = app.test_client()

    # Route: /login
    r = client.get('/login')
    assert r.status_code == 200, f"Login GET status: {r.status_code}"
    print("✓ Route /login (GET) returned 200.")

    # Route: /login POST
    r = client.post('/login', data={'email': 'recruiter@college.edu', 'password': 'admin123'}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Recruitment Intelligence Dashboard" in r.data
    print("✓ Recruiter Login (POST) successfully redirected to Dashboard.")

    # Route: /jobs
    r = client.get('/jobs')
    assert r.status_code == 200
    assert b"Job Openings" in r.data
    print("✓ Route /jobs (GET) returned 200.")

    # Route: /screen
    r = client.get('/screen?job_id=1')
    assert r.status_code == 200
    assert b"AI Resume Screening" in r.data
    print("✓ Route /screen (GET) returned 200.")

    # Route: 1-click load samples
    r = client.post('/screen/load-samples/1', follow_redirects=True)
    assert r.status_code == 200
    assert b"Loaded and screened" in r.data or b"Candidate Ranking Leaderboard" in r.data
    print("✓ Route /screen/load-samples (POST) successfully auto-loaded sample resumes!")

    # Verify Leaderboard populated
    screenings = get_screenings_for_job(1)
    assert len(screenings) >= 6, f"Expected at least 6 screenings, found {len(screenings)}"
    top_cand = screenings[0]
    print(f"✓ Ranked Leaderboard verified: #1 Candidate is '{top_cand['candidate_name']}' with {top_cand['overall_score']}% match.")

    # Route: /candidate/<id>
    r = client.get(f"/candidate/{top_cand['id']}")
    assert r.status_code == 200
    assert b"AI Evaluation Dossier" in r.data
    print(f"✓ Route /candidate/{top_cand['id']} (GET) returned 200.")

    # Route: /architecture
    r = client.get('/architecture')
    assert r.status_code == 200
    assert b"Viva" in r.data
    print("✓ Route /architecture (GET) returned 200.")

    # Route: /portal
    r = client.get('/portal')
    assert r.status_code == 200
    assert b"Applicant ATS Resume Analyzer" in r.data
    print("✓ Route /portal (GET) returned 200.")

    print("=========================================")
    print("ALL 11 SYSTEM TESTS PASSED SUCCESSFULLY! ")
    print("=========================================")

if __name__ == '__main__':
    run_tests()
