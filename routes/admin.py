"""Password-protected editing area for the shelter's own staff.

Nothing here writes to the templates. Text edits are stored as overrides
keyed by the original English wording, and lists such as events or stories
are stored as whole collections, so the site can always fall back to the
content that ships in the code.
"""

import os
import re

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

import auth
import content_index
import content_store
import site_content
from translations import TRANSLATIONS

admin_bp = Blueprint("admin", __name__)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

_ITEM_FIELD_RE = re.compile(r"^item-(?P<index>\d+)-(?P<field>[a-z_]+)$")


def _templates_root():
    return os.path.join(current_app.root_path, current_app.template_folder)


def _images_dir():
    return os.path.join(current_app.static_folder, "img")


@admin_bp.context_processor
def _inject_admin_context():
    return {
        "admin_user": auth.current_user(),
        "collections": site_content.COLLECTIONS,
    }


# ------------------------------------------------------------------ sign in

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if auth.current_user():
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        locked = auth.lockout_remaining()
        if locked:
            flash(f"Too many failed attempts. Try again in {locked // 60 + 1} minutes.", "danger")
        elif not auth.is_configured():
            flash("No editor account is set up yet. See README.md for the setup steps.", "warning")
        elif auth.attempt_login(request.form.get("username"), request.form.get("password")):
            destination = request.args.get("next") or url_for("admin.dashboard")
            if not destination.startswith("/"):
                destination = url_for("admin.dashboard")
            return redirect(destination)
        else:
            flash("Incorrect username or password.", "danger")
        return redirect(url_for("admin.login"))

    return render_template("admin/login.html", configured=auth.is_configured())


@admin_bp.route("/logout", methods=["POST"])
def logout():
    auth.logout()
    flash("You have been signed out.", "success")
    return redirect(url_for("admin.login"))


# ----------------------------------------------------------------- overview

@admin_bp.route("/")
@auth.login_required
def dashboard():
    pages = content_index.get_pages(_templates_root())
    store = content_store.load()
    edited_text = store.get("text", {})
    return render_template(
        "admin/dashboard.html",
        page_count=len(pages),
        string_count=sum(len(page["strings"]) for page in pages),
        edited_counts={lang: len(values) for lang, values in edited_text.items() if values},
        image_count=len(_list_images()),
    )


# --------------------------------------------------------------- page text

@admin_bp.route("/text")
@auth.login_required
def text_pages():
    root = _templates_root()
    pages = content_index.get_pages(root)
    store = content_store.load().get("text", {})
    summary = []
    for page in pages:
        edits = sum(
            1
            for text in page["strings"]
            for lang in ("en", "vi")
            if text in store.get(lang, {})
        )
        summary.append({**page, "edits": edits})
    return render_template("admin/text_pages.html", pages=summary)


@admin_bp.route("/text/<path:key>", methods=["GET", "POST"])
@auth.login_required
def edit_text(key):
    root = _templates_root()
    page = content_index.get_page(root, key)
    if page is None:
        flash("That page could not be found.", "danger")
        return redirect(url_for("admin.text_pages"))

    if request.method == "POST":
        edits = {"en": {}, "vi": {}}
        for index, source in enumerate(page["strings"]):
            if request.form.get(f"source-{index}") != source:
                continue
            english = (request.form.get(f"en-{index}") or "").strip()
            vietnamese = (request.form.get(f"vi-{index}") or "").strip()
            # Storing a value identical to the shipped wording would just be
            # noise, so treat "unchanged" as "no override".
            edits["en"][source] = "" if english == source else english
            shipped_vi = TRANSLATIONS.get("vi", {}).get(source, "")
            edits["vi"][source] = "" if vietnamese == shipped_vi else vietnamese
        changed = content_store.set_texts("en", edits["en"])
        changed = content_store.set_texts("vi", edits["vi"]) or changed
        flash("Your changes have been saved." if changed else "No changes to save.", "success" if changed else "info")
        return redirect(url_for("admin.edit_text", key=key))

    overrides_en = content_store.get_text("en")
    overrides_vi = content_store.get_text("vi")
    counts = content_index.usage_counts(root)
    rows = []
    for source in page["strings"]:
        rows.append(
            {
                "source": source,
                "english": overrides_en.get(source, source),
                "vietnamese": overrides_vi.get(source, TRANSLATIONS.get("vi", {}).get(source, "")),
                "edited": source in overrides_en or source in overrides_vi,
                "shared": counts.get(source, 1) > 1,
                "html": "<" in source,
            }
        )
    return render_template("admin/edit_text.html", page=page, rows=rows)


@admin_bp.route("/text/<path:key>/reset", methods=["POST"])
@auth.login_required
def reset_text(key):
    page = content_index.get_page(_templates_root(), key)
    if page is None:
        flash("That page could not be found.", "danger")
        return redirect(url_for("admin.text_pages"))
    if content_store.clear_texts(page["strings"]):
        flash("The original wording has been restored.", "success")
    else:
        flash("This page was already using the original wording.", "info")
    return redirect(url_for("admin.edit_text", key=key))


# --------------------------------------------------------------- collections

@admin_bp.route("/content/<name>", methods=["GET", "POST"])
@auth.login_required
def edit_collection(name):
    config = site_content.COLLECTIONS.get(name)
    if config is None:
        flash("That content list could not be found.", "danger")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        items = _parse_collection_form(config)
        site_content.save_items(name, items)
        flash("Your changes have been saved.", "success")
        return redirect(url_for("admin.edit_collection", name=name))

    return render_template(
        "admin/edit_collection.html",
        name=name,
        config=config,
        items=site_content.get_items(name),
        edited=site_content.is_edited(name),
        images=_list_images(),
    )


@admin_bp.route("/content/<name>/reset", methods=["POST"])
@auth.login_required
def reset_collection(name):
    if name not in site_content.COLLECTIONS:
        flash("That content list could not be found.", "danger")
        return redirect(url_for("admin.dashboard"))
    if site_content.reset_items(name):
        flash("The original entries have been restored.", "success")
    else:
        flash("This list was already using the original entries.", "info")
    return redirect(url_for("admin.edit_collection", name=name))


def _parse_collection_form(config):
    """Rebuild the list from the submitted rows, honouring order and deletes."""
    field_names = {field["name"] for field in config["fields"]}
    rows = {}
    for key, value in request.form.items():
        match = _ITEM_FIELD_RE.match(key)
        if not match:
            continue
        index = int(match.group("index"))
        field = match.group("field")
        if field not in field_names and field not in {"id", "position", "delete"}:
            continue
        rows.setdefault(index, {})[field] = value

    items = []
    for index in sorted(rows):
        row = rows[index]
        if row.get("delete"):
            continue
        entry = {field: (row.get(field) or "").strip() for field in field_names}
        if not any(entry.values()):
            continue
        if row.get("id"):
            entry["id"] = _coerce_id(row["id"])
        try:
            position = float(row.get("position") or index)
        except ValueError:
            position = index
        items.append((position, index, entry))

    items.sort(key=lambda row: (row[0], row[1]))
    return [entry for _, _, entry in items]


def _coerce_id(raw):
    return int(raw) if raw.isdigit() else raw


# -------------------------------------------------------------------- images

def _list_images():
    directory = _images_dir()
    if not os.path.isdir(directory):
        return []
    images = []
    for name in sorted(os.listdir(directory)):
        if os.path.splitext(name)[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        path = os.path.join(directory, name)
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        images.append({"name": name, "size_kb": round(size / 1024)})
    return images


@admin_bp.route("/images", methods=["GET", "POST"])
@auth.login_required
def images():
    if request.method == "POST":
        _handle_upload()
        return redirect(url_for("admin.images"))
    return render_template("admin/images.html", images=_list_images())


def _handle_upload():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        flash("Please choose an image file to upload.", "warning")
        return

    replace_target = (request.form.get("replace") or "").strip()
    if replace_target:
        filename = secure_filename(replace_target)
        target_extension = os.path.splitext(filename)[1].lower()
        source_extension = os.path.splitext(upload.filename)[1].lower()
        if source_extension != target_extension:
            flash(
                f"To replace {filename} the new file must also be a {target_extension} image.",
                "danger",
            )
            return
    else:
        filename = secure_filename(request.form.get("filename", "").strip() or upload.filename)

    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        flash("Only PNG, JPG, WEBP, GIF, and SVG images can be uploaded.", "danger")
        return

    directory = _images_dir()
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, filename)
    if os.path.exists(destination) and not replace_target:
        flash(
            f"{filename} already exists. Use the replace option if you meant to update it.",
            "warning",
        )
        return

    upload.save(destination)
    flash(f"{filename} has been saved.", "success")


@admin_bp.route("/images/delete", methods=["POST"])
@auth.login_required
def delete_image():
    filename = secure_filename(request.form.get("filename", ""))
    path = os.path.join(_images_dir(), filename)
    if filename and os.path.isfile(path):
        os.remove(path)
        flash(f"{filename} has been deleted.", "success")
    else:
        flash("That image could not be found.", "danger")
    return redirect(url_for("admin.images"))
