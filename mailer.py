"""Simple SMTP email helper for form submissions.

SMTP credentials are read from environment variables so that no secrets are
committed to the repository. Configure the following before running in
production (values shown are examples for Gmail):

    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=1
    MAIL_USERNAME=your-account@gmail.com
    MAIL_PASSWORD=your-app-password        # Gmail requires an App Password
    MAIL_SENDER=your-account@gmail.com     # optional, defaults to MAIL_USERNAME
    MAIL_RECIPIENT=tranlananh208c@gmail.com  # optional, defaults below

If SMTP is not configured, sending is skipped gracefully (the submission is
logged to the console) so the site keeps working in development.
"""

import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

DEFAULT_RECIPIENT = "tranlananh208c@gmail.com"


def _get_config():
    return {
        "server": os.environ.get("MAIL_SERVER"),
        "port": int(os.environ.get("MAIL_PORT", "587")),
        "use_tls": os.environ.get("MAIL_USE_TLS", "1") not in ("0", "false", "False", ""),
        "username": os.environ.get("MAIL_USERNAME"),
        "password": os.environ.get("MAIL_PASSWORD"),
        "sender": os.environ.get("MAIL_SENDER") or os.environ.get("MAIL_USERNAME"),
        "recipient": os.environ.get("MAIL_RECIPIENT", DEFAULT_RECIPIENT),
    }


def build_body(title, fields):
    """Build a plain-text email body from an ordered list of (label, value)."""
    lines = [title, "=" * len(title), ""]
    for label, value in fields:
        value = (value or "").strip() if isinstance(value, str) else value
        lines.append(f"{label}: {value if value else '-'}")
    return "\n".join(lines)


def send_form_email(subject, body, reply_to=None):
    """Send a form submission email. Returns True on success, False otherwise."""
    config = _get_config()

    if not (config["server"] and config["username"] and config["password"]):
        logger.warning(
            "SMTP is not configured; skipping email send.\n"
            "Subject: %s\n%s", subject, body
        )
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["sender"]
    message["To"] = config["recipient"]
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)

    try:
        with smtplib.SMTP(config["server"], config["port"], timeout=20) as smtp:
            if config["use_tls"]:
                smtp.starttls()
            smtp.login(config["username"], config["password"])
            smtp.send_message(message)
        return True
    except Exception:  # noqa: BLE001 - log and fail gracefully
        logger.exception("Failed to send form submission email.")
        return False
