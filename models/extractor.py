"""
extractor.py
Information extraction engine for resumes:
- Candidate Name detection
- Contact info (Email, Phone, LinkedIn, GitHub)
- Skill matching & categorization
- Education degree extraction
- Work experience (years & positions)
"""

import re
from datetime import datetime
from models.skills_db import ALL_SKILLS, SKILL_CATEGORIES, normalize_skill

# Regex patterns
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}|(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
LINKEDIN_REGEX = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([a-zA-Z0-9_-]+)'
GITHUB_REGEX = r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)'

EDUCATION_PATTERNS = [
    (r'\b(ph\.?d|doctor\s+of\s+philosophy|doctorate)\b', 'Ph.D'),
    (r'\b(m\.?tech|master\s+of\s+technology)\b', 'M.Tech'),
    (r'\b(m\.?s|master\s+of\s+science)\b', 'M.S.'),
    (r'\b(m\.?e|master\s+of\s+engineering)\b', 'M.E.'),
    (r'\b(mba|master\s+of\s+business\s+administration)\b', 'MBA'),
    (r'\b(mca|master\s+of\s+computer\s+applications)\b', 'MCA'),
    (r'\b(b\.?tech|bachelor\s+of\s+technology)\b', 'B.Tech'),
    (r'\b(b\.?e|bachelor\s+of\s+engineering)\b', 'B.E.'),
    (r'\b(b\.?s|bachelor\s+of\s+science)\b', 'B.S.'),
    (r'\b(bca|bachelor\s+of\s+computer\s+applications)\b', 'BCA'),
    (r'\b(bba|bachelor\s+of\s+business\s+administration)\b', 'BBA'),
    (r'\b(diploma)\b', 'Diploma'),
    (r'\b(high\s+school|12th|secondary\s+school)\b', 'High School')
]

DEGREE_HIERARCHY = {
    'Ph.D': 5,
    'M.Tech': 4,
    'M.S.': 4,
    'M.E.': 4,
    'MCA': 4,
    'MBA': 4,
    'B.Tech': 3,
    'B.E.': 3,
    'B.S.': 3,
    'BCA': 3,
    'BBA': 2,
    'Diploma': 2,
    'High School': 1
}

def extract_email(text: str) -> str:
    matches = re.findall(EMAIL_REGEX, text)
    if matches:
        return matches[0].strip()
    return ""

def extract_phone(text: str) -> str:
    matches = re.findall(PHONE_REGEX, text)
    for m in matches:
        clean = re.sub(r'[\s\-\(\)]', '', m)
        if 10 <= len(clean) <= 13:
            return m.strip()
    return ""

def extract_links(text: str) -> dict:
    links = {"linkedin": "", "github": ""}
    li = re.findall(LINKEDIN_REGEX, text, re.IGNORECASE)
    if li:
        links["linkedin"] = f"https://linkedin.com/in/{li[0]}"
    gh = re.findall(GITHUB_REGEX, text, re.IGNORECASE)
    if gh:
        links["github"] = f"https://github.com/{gh[0]}"
    return links

def extract_name(text: str) -> str:
    """
    Extract candidate's name from header lines.
    Skips labels like 'Resume', 'Curriculum Vitae', contact info, or URLs.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    ignore_words = {
        'resume', 'curriculum vitae', 'cv', 'profile', 'summary', 'contact',
        'experience', 'education', 'skills', 'objective', 'personal', 'projects',
        'page', 'page 1', 'email', 'phone', 'address', 'portfolio'
    }

    for line in lines[:8]:
        # Strip bullets or prefixes
        clean = re.sub(r'^[^a-zA-Z]+', '', line).strip()
        lower = clean.lower()

        # Skip if contains email, URL, phone digits, or obvious headings
        if '@' in lower or 'http' in lower or '.com' in lower:
            continue
        if any(w in lower for w in ignore_words):
            continue
        if len(re.findall(r'\d', clean)) > 2:
            continue

        # Check word count: typically 2 to 4 capitalized words
        words = clean.split()
        if 1 <= len(words) <= 4:
            # Check if majority of characters are alphabetic
            alpha_ratio = sum(c.isalpha() or c.isspace() for c in clean) / max(len(clean), 1)
            if alpha_ratio > 0.85:
                return clean.title()

    return "Candidate"

def extract_skills(text: str) -> dict:
    """
    Scan text against taxonomy of skills.
    Returns:
    - 'found_skills': list of normalized unique skills found
    - 'categorized': dict of category -> [skills]
    """
    text_lower = " " + text.lower() + " "
    # Replace punctuation with spaces for clean matching, but preserve special characters like +, #, .
    sanitized = re.sub(r'[^\w\s\+\#\.]', ' ', text_lower)
    sanitized = " " + re.sub(r'\s+', ' ', sanitized) + " "

    found = set()

    for skill in ALL_SKILLS:
        skill_norm = normalize_skill(skill)
        # Handle single characters or symbols (like c, r, c++)
        if skill in ['c', 'r']:
            pattern = rf'(?<=\s){re.escape(skill)}(?=\s|[,;/])'
        elif skill in ['c++', 'c#', '.net']:
            pattern = rf'(?<=\s){re.escape(skill)}(?=\s|[,;/])'
        else:
            pattern = rf'\b{re.escape(skill)}\b'

        if re.search(pattern, text_lower) or re.search(pattern, sanitized):
            found.add(skill_norm)

    # Categorize
    categorized = {}
    for cat, cat_skills in SKILL_CATEGORIES.items():
        matched_in_cat = [s for s in cat_skills if normalize_skill(s) in found]
        if matched_in_cat:
            categorized[cat] = sorted(list(set(normalize_skill(s) for s in matched_in_cat)))

    return {
        "found_skills": sorted(list(found)),
        "categorized": categorized
    }

def extract_education(text: str) -> dict:
    """
    Extract highest and all degrees identified from text.
    """
    degrees_found = []
    text_lower = text.lower()

    for pattern, name in EDUCATION_PATTERNS:
        if re.search(pattern, text_lower):
            if name not in degrees_found:
                degrees_found.append(name)

    # Determine highest degree
    highest = "Not Specified"
    max_rank = 0
    for deg in degrees_found:
        rank = DEGREE_HIERARCHY.get(deg, 0)
        if rank > max_rank:
            max_rank = rank
            highest = deg

    return {
        "highest_degree": highest,
        "degrees": degrees_found,
        "education_rank": max_rank
    }

def extract_experience_years(text: str) -> float:
    """
    Heuristic to estimate candidate's total years of experience.
    1. Looks for explicit mentions like '5+ years of experience', '3.5 yrs'.
    2. Looks for year ranges like '2019 - 2023', '2018 to Present'.
    """
    text_lower = text.lower()

    # Explicit mentions
    exp_mentions = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text_lower)
    if exp_mentions:
        try:
            years = [float(y) for y in exp_mentions if float(y) <= 40]
            if years:
                return max(years)
        except Exception:
            pass

    # Year ranges detection
    current_year = datetime.now().year
    year_ranges = re.findall(r'\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current|now)\b', text_lower)
    
    total_months = 0
    calculated_years = []
    for start, end in year_ranges:
        try:
            s_year = int(start)
            if end in ['present', 'current', 'now']:
                e_year = current_year
            else:
                e_year = int(end)
            
            if 1980 <= s_year <= current_year and s_year <= e_year <= current_year + 1:
                diff = e_year - s_year
                if 0 <= diff <= 35:
                    calculated_years.append(diff)
        except Exception:
            continue

    if calculated_years:
        # Avoid double-counting overlapping ranges simply by taking maximum span or sum cap
        estimated = sum(calculated_years)
        return min(round(estimated, 1), 30.0)

    return 0.0

def extract_full_profile(text: str, filename: str = "") -> dict:
    """
    Master function: parses all structured entities from raw resume text.
    """
    name = extract_name(text)
    if name == "Candidate" and filename:
        # Fallback to filename if text-based name is generic
        base = re.sub(r'[\-_]', ' ', filename)
        base = re.sub(r'\.(pdf|docx|txt|doc)', '', base, flags=re.I)
        base = re.sub(r'resume|cv', '', base, flags=re.I).strip()
        if len(base) >= 3:
            name = base.title()

    email = extract_email(text)
    phone = extract_phone(text)
    links = extract_links(text)
    skill_info = extract_skills(text)
    edu_info = extract_education(text)
    exp_years = extract_experience_years(text)

    # Word count and reading time
    words = len(text.split())

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": links.get("linkedin", ""),
        "github": links.get("github", ""),
        "skills": skill_info["found_skills"],
        "categorized_skills": skill_info["categorized"],
        "education": edu_info["highest_degree"],
        "all_degrees": edu_info["degrees"],
        "education_rank": edu_info["education_rank"],
        "experience_years": exp_years,
        "word_count": words,
        "raw_text": text
    }
