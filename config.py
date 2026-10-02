import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'careermatch-ai-academic-project-secret-key-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Resume Upload Folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
