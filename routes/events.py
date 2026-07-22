from flask import Blueprint, render_template

from data import EVENTS, STORIES

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
def events_list():
    return render_template("events/events.html", events=EVENTS)


@events_bp.route("/stories")
def stories():
    return render_template("events/stories.html", stories=STORIES)
