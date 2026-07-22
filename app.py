from flask import Flask
from flask_wtf.csrf import CSRFProtect

from routes import register_blueprints

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    csrf.init_app(app)
    register_blueprints(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
