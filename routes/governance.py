from flask import Blueprint, render_template

governance_bp = Blueprint("governance", __name__)


@governance_bp.route("/charter")
def charter():
    return render_template("governance/charter.html")


@governance_bp.route("/organization")
def organization():
    return render_template("governance/organization.html")
