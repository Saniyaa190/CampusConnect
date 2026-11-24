import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "campusconnect-secret-key-prod-2026-btech-project")
    
    # Serverless / Vercel environment detection
    IS_VERCEL = os.getenv("VERCEL") == "1"

    if IS_VERCEL:
        # Vercel serverless environment: root filesystem is read-only.
        # Use external DATABASE_URL if provided, else copy packaged SQLite to /tmp so writes succeed.
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            tmp_db = Path("/tmp") / "campusconnect.db"
            packaged_db = BASE_DIR / "instance" / "campusconnect.db"
            if not tmp_db.exists() and packaged_db.exists():
                import shutil
                try:
                    shutil.copy2(packaged_db, tmp_db)
                except Exception:
                    pass
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_db.as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = database_url

        UPLOAD_FOLDER = Path("/tmp") / "uploads"
        try:
            UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    else:
        db_path = BASE_DIR / "instance" / "campusconnect.db"
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")

        UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
        try:
            UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
    
    # WTForms CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
