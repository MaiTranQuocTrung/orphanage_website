from flask import Blueprint, flash, redirect, render_template, request, url_for

support_bp = Blueprint("support", __name__)

VOLUNTEER_REQUIRED_FIELDS = (
    "first_name",
    "last_name",
    "email",
    "phone",
    "volunteer_role",
    "availability",
)

SPONSORSHIP_REQUIRED_FIELDS = (
    "sponsor_name",
    "email",
    "phone",
    "sponsorship_level",
    "frequency",
)


def _missing_fields(field_names):
    return [name for name in field_names if not request.form.get(name, "").strip()]


@support_bp.route("/volunteer", methods=["GET", "POST"])
def volunteer_registration():
    if request.method == "POST":
        missing = _missing_fields(VOLUNTEER_REQUIRED_FIELDS)
        if missing or not request.form.get("agree_policy"):
            flash("Please complete all required fields and agree to the Volunteer Policy.", "danger")
        else:
            flash("Thank you for registering as a volunteer! We will contact you soon.", "success")
        return redirect(url_for("support.volunteer_registration"))
    return render_template("support/volunteer.html")


@support_bp.route("/sponsorship", methods=["GET", "POST"])
def sponsorship_registration():
    if request.method == "POST":
        missing = _missing_fields(SPONSORSHIP_REQUIRED_FIELDS)
        if missing or not request.form.get("agree_terms"):
            flash("Please complete all required fields and confirm your sponsorship interest.", "danger")
        else:
            flash("Thank you for your sponsorship interest! Our team will reach out shortly.", "success")
        return redirect(url_for("support.sponsorship_registration"))
    return render_template("support/sponsorship.html")
