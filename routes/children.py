from flask import Blueprint, render_template

children_bp = Blueprint("children", __name__)


@children_bp.route("/beneficiaries")
def beneficiaries():
    return render_template("children/beneficiaries.html")


@children_bp.route("/intake")
def intake():
    return render_template("children/intake.html")


@children_bp.route("/child-rights")
def child_rights():
    return render_template("children/child_rights.html")
