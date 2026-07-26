from flask import Blueprint, render_template

from site_content import get_events, get_stories

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def events_list():
    return render_template("events/events.html", events=get_events())


@events_bp.route("/stories")
def stories():
    return render_template("events/stories.html", stories=get_stories())
