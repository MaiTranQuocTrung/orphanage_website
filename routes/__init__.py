from flask import Flask

from .about import about_bp
from .admin import admin_bp
from .children import children_bp
from .events import events_bp
from .governance import governance_bp
from .home import home_bp
from .language import language_bp
from .policies import policies_bp
from .support import support_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(home_bp)
    app.register_blueprint(language_bp)
    app.register_blueprint(about_bp, url_prefix="/about")
    app.register_blueprint(children_bp, url_prefix="/children")
    app.register_blueprint(governance_bp, url_prefix="/governance")
    app.register_blueprint(policies_bp, url_prefix="/policies")
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(support_bp, url_prefix="/support")
    app.register_blueprint(admin_bp, url_prefix="/admin")
