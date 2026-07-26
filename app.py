import os

from flask import Flask, request, url_for
from flask_wtf.csrf import CSRFProtect

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

import auth
import content_index
import content_store
import i18n
from routes import register_blueprints

csrf = CSRFProtect()

MAX_UPLOAD_BYTES = 8 * 1024 * 1024


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    csrf.init_app(app)
    content_store.init_app(app)
    i18n.init_app(app)
    register_blueprints(app)

    def versioned_url_for(endpoint, **values):
        """Append a content version to static URLs so browsers (and Nginx's
        long-lived cache) always pick up the latest CSS/JS/images after a
        change, instead of serving a stale cached copy."""
        if endpoint == "static":
            filename = values.get("filename")
            if filename:
                file_path = os.path.join(app.static_folder, filename)
                try:
                    values["v"] = int(os.stat(file_path).st_mtime)
                except OSError:
                    pass
        return url_for(endpoint, **values)

    @app.context_processor
    def _inject_versioned_url_for():
        return {"url_for": versioned_url_for}

    @app.context_processor
    def _inject_editor_bar():
        """Signed-in staff see a bar on the public site linking straight to the
        editor screen for whichever page they are looking at."""
        if not auth.current_user() or request.blueprint == "admin":
            return {"editor_user": None, "editor_edit_url": None}
        templates_root = os.path.join(app.root_path, app.template_folder)
        key = content_index.key_for_path(templates_root, request.path)
        return {
            "editor_user": auth.current_user(),
            "editor_edit_url": url_for("admin.edit_page", key=key) if key else None,
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
