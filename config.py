import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college_project_resume_screening_secret_key_2026')
    DATABASE = os.path.join(BASE_DIR, 'database.sqlite')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    SAMPLE_FOLDER = os.path.join(BASE_DIR, 'sample_resumes')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
