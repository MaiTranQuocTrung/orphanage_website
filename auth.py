"""Password protection for the admin area.

One editor account, configured through environment variables so no credential
ever lives in the repository. If nothing is configured the admin area refuses
every login, which keeps a fresh deployment closed by default.
"""

import functools
import hmac
import os
import time

from flask import flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

SESSION_KEY = "admin_user"

# Lock an address out after this many failures, for this long.
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60

_attempts = {}


def _username():
    return os.environ.get("ADMIN_USERNAME", "").strip()


def is_configured():
    return bool(_username()) and bool(
        os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
        or os.environ.get("ADMIN_PASSWORD", "").strip()
    )


def _password_matches(password):
    hashed = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
    if hashed:
        try:
            return check_password_hash(hashed, password)
        except ValueError:
            return False
    plain = os.environ.get("ADMIN_PASSWORD", "").strip()
    if plain:
        return hmac.compare_digest(plain, password)
    return False


def hash_password(password):
    return generate_password_hash(password)


def _client_key():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


def lockout_remaining():
    """Seconds until this client may try again, or 0 if it may try now."""
    record = _attempts.get(_client_key())
    if not record:
        return 0
    count, last = record
    if count < MAX_ATTEMPTS:
        return 0
    remaining = int(LOCKOUT_SECONDS - (time.time() - last))
    if remaining <= 0:
        _attempts.pop(_client_key(), None)
        return 0
    return remaining


def _record_failure():
    key = _client_key()
    count, last = _attempts.get(key, (0, 0.0))
    if time.time() - last > LOCKOUT_SECONDS:
        count = 0
    _attempts[key] = (count + 1, time.time())


def attempt_login(username, password):
    """Validate credentials and start a session. Returns True on success."""
    if not is_configured():
        return False
    expected = _username()
    ok = hmac.compare_digest(expected, (username or "").strip()) and _password_matches(password or "")
    if not ok:
        _record_failure()
        return False
    _attempts.pop(_client_key(), None)
    session[SESSION_KEY] = expected
    return True


def logout():
    session.pop(SESSION_KEY, None)


def current_user():
    return session.get(SESSION_KEY)


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("admin.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped
