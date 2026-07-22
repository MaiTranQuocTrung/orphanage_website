from flask import Blueprint, render_template

policies_bp = Blueprint("policies", __name__)


@policies_bp.route("/rules")
def rules():
    return render_template("policies/rules.html")


@policies_bp.route("/visitor")
def visitor():
    return render_template("policies/visitor.html")


@policies_bp.route("/volunteer")
def volunteer():
    return render_template("policies/volunteer_policy.html")


@policies_bp.route("/child-protection")
def child_protection():
    return render_template("policies/child_protection.html")
