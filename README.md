# AI-Powered Resume Screening & Ranking System

An end-to-end, production-grade automated recruitment intelligence platform built from scratch in Python. It parses candidate resumes in multiple formats (PDF, DOCX, TXT), extracts named entities (Name, Contact Details, Skills, Education, Work Tenure), and ranks candidates using TF-IDF vectorization, Cosine Similarity, and multi-factor weighted scoring.

---

## 🌟 Key Features

1. **Authentication & Role-Based Access**:
   - Recruiter / HR Mode: Post job openings, set custom weightings, upload bulk resumes, and view the ranked leaderboard.
   - Candidate / Applicant Mode: Upload a resume to test ATS compatibility, identify missing skills, and receive actionable suggestions.
   - **1-Click Evaluator Login**: Quick-fill demo credentials on the sign-in page for instant testing.

2. **Multi-Format Document Parsing**:
   - Supports **PDF** (`.pdf`), **Microsoft Word** (`.docx`), and **Plain Text** (`.txt`) documents with automatic character encoding and stream fallback.

3. **Intelligent Information Extraction**:
   - **Candidate Name & Contact Info**: Extracts Name, Email, Phone number, LinkedIn, and GitHub links.
   - **Curated Skills Taxonomy**: Matches against a structured taxonomy across Programming Languages, Web Frameworks, AI/ML, Cloud/DevOps, Databases, and Soft Skills.
   - **Education Level**: Recognizes and ranks degrees (Ph.D, M.Tech, M.S., B.Tech, BCA, High School).
   - **Work Tenure**: Heuristically calculates total experience years from dates and explicit tenure mentions.

4. **Multi-Factor AI Ranking Engine**:
   - **TF-IDF + Cosine Similarity**: Evaluates semantic alignment in vector space using unigrams and bigrams.
   - **Skill Coverage Jaccard Ratio**: Calculates exact match rate against mandatory skills.
   - **Tenure & Qualification Benchmarking**: Evaluates candidates against minimum required years of experience and degrees.
   - **Configurable Criterion Weights**: Recruiters can customize weights for Skills, Semantics, Experience, and Education.

5. **Explainable AI (XAI) Candidate Dossier**:
   - Transparent sub-score metrics (Overall, Technical Skills %, Semantic %, Experience %, Education %).
   - Bulleted AI strengths and missing skill gap matrix (Matched, Missing, and Bonus skills).
   - Clear hiring recommendation (Strong Hire, Shortlisted, Under Review, Not Recommended).
   - Export candidate ranking leaderboard to CSV format or print dossier to PDF.

6. **Pre-Packaged Instant Test Resumes**:
   - Includes 6 diverse pre-generated candidate resumes in PDF, DOCX, and TXT formats inside the `sample_resumes/` folder.
   - 1-Click "Auto-Load Sample Resumes" button on the screening workbench for instant demonstration.

---

## 📁 Project Structure

```
resume-screening-system/
├── app.py                     # Main Flask server and route controllers
├── config.py                  # Project configuration and storage paths
├── database.py                # SQLite database management and queries
├── create_sample_resumes.py   # Script that generated sample PDF/DOCX/TXT resumes
├── requirements.txt           # Python dependencies
├── models/
│   ├── parser.py              # Multi-format resume text parser (PDF, DOCX, TXT)
│   ├── extractor.py           # Contact, Degree, Experience, and Skill extractor
│   ├── skills_db.py           # Structured skills database and aliases
│   └── ranker.py              # TF-IDF + Cosine Similarity and Multi-Factor Scorer
├── sample_resumes/            # Pre-generated candidate resumes for testing
├── static/
│   ├── css/
│   │   └── style.css          # Custom, clean, human-designed stylesheet
│   └── js/
│       └── main.js            # Client-side interactions (drag & drop, live search)
└── templates/
    ├── base.html              # Base layout with navbar and footer
    ├── login.html             # Login page with 1-click quick demo buttons
    ├── register.html          # User registration
    ├── dashboard.html         # Recruiter KPI overview and vacancy metrics
    ├── jobs.html              # Job posting manager and weighting configuration
    ├── screen.html            # Main screening workbench and ranked leaderboard
    ├── candidate_view.html    # Detailed candidate dossier and score gauges
    ├── candidate_portal.html  # Candidate self-service ATS review portal
    └── architecture.html      # Technical pipeline documentation and college viva guide
```

---

## 🚀 How to Run the Project

### 1. Prerequisites
Python 3.10+ (tested and verified on Python 3.14).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Application
```bash
python app.py
```

### 4. Open in Browser
Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Default Login Credentials

You can log in manually or use the **1-Click Quick Login** buttons on the sign-in page:

| Role | Email | Password |
|---|---|---|
| **Recruiter / Evaluator** | `recruiter@college.edu` | `admin123` |
| **Job Applicant** | `candidate@college.edu` | `admin123` |

---

## 🧪 Testing the Screening Engine

1. Sign in as **Recruiter** (`recruiter@college.edu`).
2. Navigate to **Screen & Rank** from the top navbar.
3. Select any target role (e.g. *AI / Machine Learning Engineer*).
4. Click **"⚡ Auto-Load Sample Resumes"** to screen all 6 pre-packaged candidates at once, or drag and drop any file from the `sample_resumes/` folder.
5. Inspect the sorted leaderboard with match scores, skill pills, and badges.
6. Click **"View Dossier &rarr;"** on any candidate to inspect the Explainable AI score breakdown, matched vs missing skills, and hiring recommendations.
7. Click **"📥 Export CSV"** to download the ranked results.

---

## 🎓 College Viva Defense & Technical Q&A

- **Why use TF-IDF rather than basic keyword counts?**
  Basic keyword counts inflate common words like "the", "developer", or "project". TF-IDF computes the product of Term Frequency (local importance) and Inverse Document Frequency (corpus specificity), ensuring that rare, high-value technical terms (e.g., "PyTorch", "Kubernetes") carry significant weight.
- **Why is Cosine Similarity chosen over Euclidean Distance?**
  Euclidean distance scales with document length—a verbose 4-page resume will be mathematically far from a concise job description. Cosine similarity evaluates the angle between high-dimensional vector representations, measuring semantic overlap independent of length.
- **How does the system prevent keyword stuffing?**
  The system uses multi-factor weighting: Skill Coverage (45%), TF-IDF Semantic Similarity (25%), Work Tenure (15%), and Education Degree (15%). Even if an applicant stuffs keywords, lack of verified tenure or appropriate degree automatically penalizes the composite score.
