from flask import Blueprint, render_template

from data import ORG_CHART
from site_content import get_council

about_bp = Blueprint("about", __name__)


@about_bp.route("/history")
def history():
    return render_template("about/history.html")


@about_bp.route("/vision")
def vision():
    return render_template("about/vision.html")


@about_bp.route("/council")
def council():
    return render_template("about/council.html", council_members=get_council())


@about_bp.route("/org-chart")
def org_chart():
    return render_template("about/org_chart.html", org_chart=ORG_CHART)
