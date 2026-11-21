import os
import tempfile
import pathlib
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_SERVERLESS = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'campusconnect-dev-secret-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MySQL connection configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'campusconnect')
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    ALLOW_SQLITE_FALLBACK = os.getenv('ALLOW_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't', 'yes')

    # Custom DATABASE_URL override if explicitly provided
    custom_db_url = os.getenv('DATABASE_URL')
    if custom_db_url:
        # Normalize dialect prefixes for SQLAlchemy compatibility
        if custom_db_url.startswith("postgres://"):
            custom_db_url = custom_db_url.replace("postgres://", "postgresql://", 1)
        elif custom_db_url.startswith("mysql://"):
            custom_db_url = custom_db_url.replace("mysql://", "mysql+pymysql://", 1)
        SQLALCHEMY_DATABASE_URI = custom_db_url
    elif IS_SERVERLESS:
        # In serverless environments (Vercel) without external DATABASE_URL, default to SQLite in /tmp
        tmp_db = os.path.join(tempfile.gettempdir(), 'campusconnect.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{pathlib.Path(tmp_db).as_posix()}"
    else:
        # Build standard MySQL 8 URI with PyMySQL
        encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''
        auth_part = f"{DB_USERNAME}:{encoded_password}" if encoded_password else DB_USERNAME
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{auth_part}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )

    # Engine options for connection pooling and health checks (disabled for SQLite)
    if (custom_db_url and custom_db_url.startswith('sqlite')) or IS_SERVERLESS:
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 280,
            'pool_pre_ping': True,
        }

    # Session cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration using an in-memory SQLite database."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    ALLOW_SQLITE_FALLBACK = os.getenv('ALLOW_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't', 'yes')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't', 'yes')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
