from flask import Blueprint, flash, redirect, render_template, request, url_for

support_bp = Blueprint("support", __name__)


@support_bp.route("/volunteer", methods=["GET", "POST"])
def volunteer_registration():
    if request.method == "POST":
        flash("Thank you for registering as a volunteer! We will contact you soon.", "success")
        return redirect(url_for("support.volunteer_registration"))
    return render_template("support/volunteer.html")


@support_bp.route("/sponsorship", methods=["GET", "POST"])
def sponsorship_registration():
    if request.method == "POST":
        flash("Thank you for your sponsorship interest! Our team will reach out shortly.", "success")
        return redirect(url_for("support.sponsorship_registration"))
    return render_template("support/sponsorship.html")
