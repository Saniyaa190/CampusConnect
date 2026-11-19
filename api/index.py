import os
import sys

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app

# Create production application instance for Vercel Serverless Functions
env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(env_name)
