import os

from flask import Flask
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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
