import os
import sys

# Ensure repository root and execution paths are on sys.path
api_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(api_dir)
cwd = os.getcwd()

for path_entry in (repo_root, cwd, "/var/task", api_dir):
    if path_entry and os.path.exists(path_entry) and path_entry not in sys.path:
        sys.path.insert(0, path_entry)

# Signal serverless execution environment
os.environ['VERCEL'] = '1'

try:
    from app import create_app

    env_name = os.getenv('FLASK_ENV', 'production')
    app = create_app(env_name)
    application = app
except Exception as e:
    import traceback
    err_trace = traceback.format_exc()
    print("FATAL ERROR DURING VERCEL STARTUP:\n" + err_trace)

    from flask import Flask, Response
    app = Flask(__name__)
    application = app

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return Response(
            f"<h1>CampusConnect — Server Startup Error</h1>"
            f"<p>The application encountered an error during initialization on Vercel:</p>"
            f"<pre style='background:#f4f4f4;padding:15px;border-radius:8px;overflow:auto;color:#c00;'>{err_trace}</pre>",
            mimetype="text/html",
            status=500
        )
