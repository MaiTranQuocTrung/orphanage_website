import os

from flask import Flask, url_for
from flask_wtf.csrf import CSRFProtect

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

import i18n
from routes import register_blueprints

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    csrf.init_app(app)
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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
