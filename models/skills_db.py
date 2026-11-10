"""
skills_db.py
Curated and comprehensive taxonomy of technical and domain skills
categorized for skill-matching, normalization, and gap analysis.
"""

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "c", "javascript", "typescript",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
        "r", "matlab", "dart", "perl", "bash", "shell", "powershell", "lua", "sql"
    ],
    "Web & Backend Frameworks": [
        "django", "flask", "fastapi", "spring", "spring boot", "express",
        "express.js", "nodejs", "node.js", "nest.js", "nestjs", "laravel",
        "rails", "ruby on rails", "asp.net", ".net", ".net core", "fastify",
        "koa", "rest api", "graphql", "grpc", "soap", "microservices"
    ],
    "Frontend & Mobile": [
        "react", "react.js", "react native", "next.js", "nextjs", "vue",
        "vue.js", "angular", "angularjs", "svelte", "html", "html5", "css",
        "css3", "sass", "scss", "tailwind", "tailwind css", "bootstrap",
        "redux", "zustand", "flutter", "android", "ios", "webpack", "vite"
    ],
    "Data Science & AI / ML": [
        "machine learning", "deep learning", "artificial intelligence", "nlp",
        "natural language processing", "computer vision", "tensorflow", "pytorch",
        "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "opencv", "transformers", "huggingface",
        "llm", "large language models", "langchain", "rag", "xgboost",
        "lightgbm", "random forest", "neural networks", "bert", "gpt",
        "data analysis", "data visualization", "predictive modeling"
    ],
    "Databases & Storage": [
        "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
        "cassandra", "elasticsearch", "oracle", "mariadb", "dynamodb",
        "neo4j", "firebase", "firestore", "prisma", "sqlalchemy", "hibernate"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "google cloud", "gcp",
        "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "github actions",
        "gitlab ci", "terraform", "ansible", "linux", "ubuntu", "nginx",
        "apache", "serverless", "cloudformation", "prometheus", "grafana"
    ],
    "Big Data & Analytics": [
        "spark", "apache spark", "hadoop", "kafka", "apache kafka", "airflow",
        "apache airflow", "snowflake", "bigquery", "databricks", "dbt",
        "power bi", "tableau", "excel", "etl"
    ],
    "Tools & Methodologies": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "tdd", "unit testing", "pytest",
        "jest", "selenium", "postman", "swagger", "docker-compose"
    ],
    "Soft Skills & Leadership": [
        "problem solving", "team leadership", "communication", "teamwork",
        "critical thinking", "project management", "time management",
        "mentorship", "collaboration", "adaptability", "analytical skills"
    ]
}

# Flat set of all known lowercase skill strings for fast exact/ngram matching
ALL_SKILLS = set()
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        ALL_SKILLS.add(skill.lower())

# Common aliases / normalizations
SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "sklearn": "scikit-learn",
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "postgres": "postgresql",
    "node": "node.js",
    "reactjs": "react",
    "vuejs": "vue",
    "next": "next.js",
    "tailwind": "tailwind css",
    "aws services": "aws",
    "gcp cloud": "google cloud",
    "ci / cd": "ci/cd",
    "cicd": "ci/cd"
}

def normalize_skill(skill: str) -> str:
    s = skill.strip().lower()
    return SKILL_ALIASES.get(s, s)
