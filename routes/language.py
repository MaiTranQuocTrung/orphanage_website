from flask import Blueprint, redirect, request, session, url_for

from i18n import LANGUAGES

language_bp = Blueprint("language", __name__)


@language_bp.route("/lang/<lang>")
def set_language(lang):
    if lang in LANGUAGES:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home.index"))
