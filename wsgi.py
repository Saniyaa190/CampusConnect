import os
from app import create_app

# WSGI production application instance
env_name = os.getenv('FLASK_ENV', 'production')
app = create_app(env_name)
application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port)
