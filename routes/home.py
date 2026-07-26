from flask import Blueprint, render_template

from site_content import get_recent_events, get_recent_stories

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template(
        "home/index.html",
        recent_events=get_recent_events(3),
        recent_stories=get_recent_stories(3),
    )
