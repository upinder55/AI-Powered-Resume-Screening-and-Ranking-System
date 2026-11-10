"""
ranker.py
Multi-factor AI Resume Screening & Ranking Engine:
1. TF-IDF + Cosine Similarity (Vector Space Model for semantic text relevance)
2. Exact & Fuzzy Skill Match Ratio (Jaccard-based coverage)
3. Experience Alignment Score
4. Education Qualification Score
5. Weighted Multi-Criterion Synthesis
6. Explainable AI Feedback & Recommendation Generation
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.extractor import DEGREE_HIERARCHY, extract_skills
from models.skills_db import normalize_skill

DEFAULT_WEIGHTS = {
    "skill_weight": 0.45,
    "semantic_weight": 0.25,
    "experience_weight": 0.15,
    "education_weight": 0.15
}

def compute_semantic_similarity(job_text: str, resume_text: str) -> float:
    """
    Computes cosine similarity between Job Description and Resume
    using TF-IDF n-grams (1, 2) vectorization.
    """
    if not job_text.strip() or not resume_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Normalize to 0 - 100 scale
        return round(float(sim) * 100, 2)
    except Exception:
        return 0.0

def evaluate_skills(job_skills: list, resume_skills: list) -> dict:
    """
    Compares candidate skills against required job skills.
    Returns:
    - match_percentage: 0 to 100
    - matched_skills: list
    - missing_skills: list
    - bonus_skills: list
    """
    job_skills_norm = set(normalize_skill(s) for s in job_skills if s.strip())
    resume_skills_norm = set(normalize_skill(s) for s in resume_skills if s.strip())

    if not job_skills_norm:
        # If no explicit job skills were specified, give a baseline if candidate has skills
        return {
            "match_percentage": 75.0 if resume_skills_norm else 50.0,
            "matched_skills": list(resume_skills_norm),
            "missing_skills": [],
            "bonus_skills": []
        }

    matched = sorted(list(job_skills_norm.intersection(resume_skills_norm)))
    missing = sorted(list(job_skills_norm - resume_skills_norm))
    bonus = sorted(list(resume_skills_norm - job_skills_norm))

    score = (len(matched) / len(job_skills_norm)) * 100.0

    return {
        "match_percentage": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "bonus_skills": bonus[:10]  # Show top 10 bonus skills
    }

def evaluate_experience(candidate_years: float, required_years: float) -> float:
    """
    Scores candidate experience relative to required experience.
    """
    if required_years <= 0:
        return 100.0

    if candidate_years >= required_years:
        # Full score + slight reward up to 100
        return 100.0

    # Linear penalty for lacking years
    ratio = candidate_years / required_years
    return round(ratio * 100.0, 2)

def evaluate_education(candidate_degree: str, required_degree: str) -> float:
    """
    Scores candidate highest degree against job requirement.
    """
    if not required_degree or required_degree.lower() in ["any", "not specified", "none"]:
        return 100.0

    req_rank = DEGREE_HIERARCHY.get(required_degree, 2)
    cand_rank = DEGREE_HIERARCHY.get(candidate_degree, 1)

    if cand_rank >= req_rank:
        return 100.0
    elif cand_rank == req_rank - 1:
        return 80.0
    elif cand_rank == req_rank - 2:
        return 60.0
    else:
        return 40.0

def generate_ai_insights(score: float, skill_data: dict, exp_score: float, edu_score: float, candidate_data: dict, job_data: dict) -> dict:
    """
    Generates explainable human-readable recommendations and summary.
    """
    strengths = []
    weaknesses = []

    # Analyze skills
    matched_cnt = len(skill_data["matched_skills"])
    missing_cnt = len(skill_data["missing_skills"])

    if matched_cnt > 0:
        top_skills = ", ".join(skill_data["matched_skills"][:4])
        strengths.append(f"Demonstrates key domain skills: {top_skills}.")
    
    if skill_data["match_percentage"] >= 80:
        strengths.append(f"High technical stack alignment ({skill_data['match_percentage']}%) with required criteria.")
    elif skill_data["match_percentage"] < 50:
        weaknesses.append(f"Low required skill coverage ({skill_data['match_percentage']}%). Missing: {', '.join(skill_data['missing_skills'][:4])}.")
    elif missing_cnt > 0:
        weaknesses.append(f"Lacks proficiency or mention of {', '.join(skill_data['missing_skills'][:3])}.")

    # Analyze experience
    cand_exp = candidate_data.get("experience_years", 0)
    req_exp = job_data.get("min_experience", 0)
    if exp_score >= 100:
        strengths.append(f"Meets or exceeds required experience ({cand_exp} yrs vs {req_exp} yrs required).")
    else:
        weaknesses.append(f"Experience shortfall: has {cand_exp} yrs out of {req_exp} yrs required.")

    # Analyze education
    cand_edu = candidate_data.get("education", "Not specified")
    req_edu = job_data.get("min_education", "Any")
    if edu_score >= 100:
        strengths.append(f"Satisfies educational prerequisite ({cand_edu}).")
    elif cand_edu != "Not specified":
        weaknesses.append(f"Holds {cand_edu}; preferred qualification was {req_edu}.")

    # Verdict & Hiring Recommendation
    if score >= 75:
        verdict = "Strong Hire"
        badge_class = "badge-success"
        recommendation = "Highly recommended for technical interview. Candidate exhibits comprehensive alignment with job requirements."
    elif score >= 60:
        verdict = "Shortlisted"
        badge_class = "badge-primary"
        recommendation = "Good candidate profile. Recommended for preliminary screening to verify core technical skills."
    elif score >= 45:
        verdict = "Under Review"
        badge_class = "badge-warning"
        recommendation = "Borderline candidate. Review specific project portfolios or explore transferable skill sets."
    else:
        verdict = "Not Recommended"
        badge_class = "badge-danger"
        recommendation = "Candidate profile does not satisfy baseline technical requirements or experience levels for this position."

    return {
        "verdict": verdict,
        "badge_class": badge_class,
        "recommendation": recommendation,
        "strengths": strengths if strengths else ["Basic profile uploaded without notable standouts."],
        "weaknesses": weaknesses if weaknesses else ["No critical disqualifiers identified."]
    }

def rank_candidate(candidate_profile: dict, job: dict, weights: dict = None) -> dict:
    """
    Ranks a single candidate against a job specification.
    """
    w = weights if weights else DEFAULT_WEIGHTS

    # 1. Semantic Similarity
    full_job_desc = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))}"
    semantic_score = compute_semantic_similarity(full_job_desc, candidate_profile.get("raw_text", ""))

    # 2. Skill Match
    skill_eval = evaluate_skills(job.get("required_skills", []), candidate_profile.get("skills", []))
    skill_score = skill_eval["match_percentage"]

    # 3. Experience Match
    exp_score = evaluate_experience(candidate_profile.get("experience_years", 0), job.get("min_experience", 0))

    # 4. Education Match
    edu_score = evaluate_education(candidate_profile.get("education", ""), job.get("min_education", ""))

    # 5. Composite Score
    composite_score = (
        (skill_score * w.get("skill_weight", 0.45)) +
        (semantic_score * w.get("semantic_weight", 0.25)) +
        (exp_score * w.get("experience_weight", 0.15)) +
        (edu_score * w.get("education_weight", 0.15))
    )
    composite_score = round(min(max(composite_score, 0.0), 100.0), 1)

    # 6. Generate explainable AI feedback
    insights = generate_ai_insights(composite_score, skill_eval, exp_score, edu_score, candidate_profile, job)

    return {
        "overall_score": composite_score,
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "exp_score": exp_score,
        "edu_score": edu_score,
        "matched_skills": skill_eval["matched_skills"],
        "missing_skills": skill_eval["missing_skills"],
        "bonus_skills": skill_eval["bonus_skills"],
        "verdict": insights["verdict"],
        "badge_class": insights["badge_class"],
        "recommendation": insights["recommendation"],
        "strengths": insights["strengths"],
        "weaknesses": insights["weaknesses"]
    }
