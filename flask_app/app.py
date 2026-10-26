import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# ============================================================
# FLASK
# ============================================================

from flask import Flask
from flask_cors import CORS


# ============================================================
# CREATE APP
# ============================================================

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)


# ============================================================
# CORS
# ============================================================

CORS(app)


# ============================================================
# FILE UPLOAD LIMIT
# ============================================================

app.config["MAX_CONTENT_LENGTH"] = (
    50 * 1024 * 1024
)


# ============================================================
# REGISTER ROUTES
# ============================================================

from flask_app.routes import register_routes

register_routes(app)


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("PERSONAL AI WORK ASSISTANT")
    print("=" * 60)
    print("Server: http://127.0.0.1:5000")
    print("Health: http://127.0.0.1:5000/health")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,

        # Important:
        # Do NOT automatically reload when
        # transformers/sentence-transformers
        # files change.
        debug=False,
        use_reloader=False
    )