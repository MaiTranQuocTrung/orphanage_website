from flask import Blueprint, render_template

from data import FOUNDING_COUNCIL, ORG_CHART

about_bp = Blueprint("about", __name__)


@about_bp.route("/history")
def history():
    return render_template("about/history.html")


@about_bp.route("/vision")
def vision():
    return render_template("about/vision.html")


@about_bp.route("/charter")
def charter():
    return render_template("about/charter.html")


@about_bp.route("/organization")
def organization():
    return render_template("about/organization.html")


@about_bp.route("/council")
def council():
    return render_template("about/council.html", council_members=FOUNDING_COUNCIL)


@about_bp.route("/org-chart")
def org_chart():
    return render_template("about/org_chart.html", org_chart=ORG_CHART)
