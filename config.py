
import os
from pathlib import Path
from dotenv import load_dotenv
def normalize_database_url(url):
    if url.startswith("postgres://"):
        return url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )

    if url.startswith("postgresql://"):
        return url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    return url
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "campusconnect-secret-key-change-in-production"
    )

    IS_VERCEL = os.getenv("VERCEL") == "1"

    database_url = os.getenv("DATABASE_URL")

    if IS_VERCEL:
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is missing. "
                "Configure a PostgreSQL database in Vercel."
            )

        # Normalize PostgreSQL URL for psycopg 3
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

        SQLALCHEMY_DATABASE_URI = database_url

        UPLOAD_FOLDER = Path("/tmp/uploads")
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    else:
        db_path = BASE_DIR / "instance" / "campusconnect.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            f"sqlite:///{db_path.as_posix()}"
        )

        UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "png", "jpg", "jpeg", "webp", "gif"
    }

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
