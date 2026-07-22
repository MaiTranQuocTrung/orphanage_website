from flask import Blueprint, flash, redirect, render_template, request, url_for

from mailer import build_body, send_form_email

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
    "amount",
    "currency",
    "frequency",
)

# Friendly labels for form fields used when composing notification emails.
FIELD_LABELS = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "sponsor_name": "Full Name",
    "organization": "Organization",
    "email": "Email",
    "phone": "Phone",
    "volunteer_role": "Preferred Role",
    "availability": "Weekly Availability",
    "start_date": "Preferred Start Date",
    "experience": "Relevant Experience",
    "sponsorship_level": "Sponsorship Level",
    "amount": "Contribution Amount",
    "currency": "Currency",
    "frequency": "Payment Frequency",
    "preference": "Child Preference",
    "message": "Message",
}

# Fields never included in emails (security tokens and consent checkboxes).
_EXCLUDED_FIELDS = {"csrf_token", "agree_policy", "agree_terms"}


def _missing_fields(field_names):
    return [name for name in field_names if not request.form.get(name, "").strip()]


def _collect_fields():
    """Build an ordered (label, value) list from the submitted form."""
    fields = []
    for name in request.form:
        if name in _EXCLUDED_FIELDS:
            continue
        label = FIELD_LABELS.get(name, name.replace("_", " ").title())
        fields.append((label, request.form.get(name)))
    return fields


@support_bp.route("/volunteer", methods=["GET", "POST"])
def volunteer_registration():
    if request.method == "POST":
        missing = _missing_fields(VOLUNTEER_REQUIRED_FIELDS)
        if missing or not request.form.get("agree_policy"):
            flash("Please complete all required fields and agree to the Volunteer Policy.", "danger")
        else:
            body = build_body("New Volunteer Registration", _collect_fields())
            send_form_email(
                subject="New Volunteer Registration - Tuệ Quang Shelter",
                body=body,
                reply_to=request.form.get("email"),
            )
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
            body = build_body("New Sponsorship Interest", _collect_fields())
            send_form_email(
                subject="New Sponsorship Interest - Tuệ Quang Shelter",
                body=body,
                reply_to=request.form.get("email"),
            )
            flash("Thank you for your sponsorship interest! Our team will reach out shortly.", "success")
        return redirect(url_for("support.sponsorship_registration"))
    return render_template("support/sponsorship.html")
