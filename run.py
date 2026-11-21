import os
import sys
from app import create_app

# Create application instance using environment configuration
env_name = os.getenv('FLASK_ENV', 'development')
app = create_app(env_name)
application = app

if __name__ == '__main__':
    # Allow passing CLI arguments like 'seed-events' or 'create-admin' directly through run.py
    if len(sys.argv) > 1 and sys.argv[1] in ('seed-events', 'create-admin', 'init-db'):
        # Invoke flask cli directly
        with app.app_context():
            from app import register_cli_commands
            # Let Flask cli handle the command
            app.cli.main(args=sys.argv[1:])
    else:
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '127.0.0.1')
        print(f"\n==================================================")
        print(f"  CampusConnect — College Event Management System  ")
        print(f"==================================================")
        print(f"  Running on: http://{host}:{port}/")
        print(f"  Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1]}")
        print(f"  Press CTRL+C to quit.")
        print(f"==================================================\n")
        app.run(host=host, port=port, debug=app.config.get('DEBUG', True))
