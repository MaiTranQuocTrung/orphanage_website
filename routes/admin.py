"""Password-protected editing area for the shelter's own staff.

The editor is organised around the pages of the website: pick a page, change
its wording and its entries, save. Nothing here writes to the templates. Text
edits are stored as overrides keyed by the original English wording, and lists
such as events or stories are stored as whole collections, so the site can
always fall back to the content that ships in the code.
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
    return {"admin_user": auth.current_user()}


# ------------------------------------------------------------------ sign in

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if auth.current_user():
        return redirect(url_for("admin.pages"))

    if request.method == "POST":
        locked = auth.lockout_remaining()
        if locked:
            flash(f"Too many failed attempts. Try again in {locked // 60 + 1} minutes.", "danger")
        elif not auth.is_configured():
            flash("No editor account is set up yet. See README.md for the setup steps.", "warning")
        elif auth.attempt_login(request.form.get("username"), request.form.get("password")):
            destination = request.args.get("next") or url_for("admin.pages")
            if not destination.startswith("/"):
                destination = url_for("admin.pages")
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


# ---------------------------------------------------------------- page list

@admin_bp.route("/")
@auth.login_required
def pages():
    root = _templates_root()
    edits = content_store.load().get("text", {})
    sections = []
    for section in content_index.get_sections(root):
        entries = []
        for page in section["pages"]:
            changed = sum(
                1
                for text in page["strings"]
                for lang in ("en", "vi")
                if text in edits.get(lang, {})
            )
            name, _config = site_content.collection_for_page(page["key"])
            entries.append({**page, "changed": changed, "collection": name})
        sections.append({"label": section["label"], "pages": entries})
    return render_template("admin/pages.html", sections=sections)


# -------------------------------------------------------------- page editor

@admin_bp.route("/page/<path:key>", methods=["GET", "POST"])
@auth.login_required
def edit_page(key):
    root = _templates_root()
    page = content_index.get_page(root, key)
    if page is None:
        flash("That page could not be found.", "danger")
        return redirect(url_for("admin.pages"))

    collection_name, collection = site_content.collection_for_page(key)

    if request.method == "POST":
        changed = _save_text(page)
        if collection_name:
            items = site_content.assign_ids(collection_name, _parse_collection_form(collection))
            if items != site_content.get_items(collection_name):
                site_content.save_items(collection_name, items)
                changed = True
        flash("Your changes have been saved." if changed else "No changes to save.",
              "success" if changed else "info")
        return redirect(url_for("admin.edit_page", key=key))

    overrides_en = content_store.get_text("en")
    overrides_vi = content_store.get_text("vi")
    counts = content_index.usage_counts(root)
    rows = []
    for entry in page["entries"]:
        source = entry["text"]
        rows.append(
            {
                "source": source,
                "role": entry["role"],
                "english": overrides_en.get(source, source),
                "vietnamese": overrides_vi.get(source, TRANSLATIONS.get("vi", {}).get(source, "")),
                "changed": source in overrides_en or source in overrides_vi,
                "shared": counts.get(source, 1) > 1,
                "long": len(source) > 90,
            }
        )

    return render_template(
        "admin/edit_page.html",
        page=page,
        rows=rows,
        collection_name=collection_name,
        collection=collection,
        items=site_content.get_items(collection_name) if collection_name else [],
        collection_changed=site_content.is_edited(collection_name) if collection_name else False,
        photos=_list_photos(),
    )


def _save_text(page):
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
    return content_store.set_texts("vi", edits["vi"]) or changed


@admin_bp.route("/page/<path:key>/restore", methods=["POST"])
@auth.login_required
def restore_page(key):
    page = content_index.get_page(_templates_root(), key)
    if page is None:
        flash("That page could not be found.", "danger")
        return redirect(url_for("admin.pages"))

    restored = content_store.clear_texts(page["strings"])
    collection_name, _config = site_content.collection_for_page(key)
    if collection_name and site_content.reset_items(collection_name):
        restored = True
    flash(
        "The original content has been restored." if restored
        else "This page was already showing its original content.",
        "success" if restored else "info",
    )
    return redirect(url_for("admin.edit_page", key=key))


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


# -------------------------------------------------------------------- photos

def _list_photos():
    directory = _images_dir()
    if not os.path.isdir(directory):
        return []
    photos = []
    for name in sorted(os.listdir(directory)):
        if os.path.splitext(name)[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        path = os.path.join(directory, name)
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        photos.append({"name": name, "size_kb": round(size / 1024)})
    return photos


@admin_bp.route("/photos", methods=["GET", "POST"])
@auth.login_required
def photos():
    if request.method == "POST":
        _handle_upload()
        return redirect(url_for("admin.photos"))
    return render_template("admin/photos.html", photos=_list_photos())


def _handle_upload():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        flash("Please choose a photo to upload.", "warning")
        return

    replace_target = (request.form.get("replace") or "").strip()
    if replace_target:
        filename = secure_filename(replace_target)
        target_extension = os.path.splitext(filename)[1].lower()
        source_extension = os.path.splitext(upload.filename)[1].lower()
        if source_extension != target_extension:
            flash(
                f"To replace {filename} the new photo must also be a {target_extension} file.",
                "danger",
            )
            return
    else:
        filename = secure_filename(request.form.get("filename", "").strip() or upload.filename)

    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        flash("Only PNG, JPG, WEBP, GIF, and SVG photos can be uploaded.", "danger")
        return

    directory = _images_dir()
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, filename)
    if os.path.exists(destination) and not replace_target:
        flash(
            f"{filename} already exists. Choose it under \"Replace\" if you meant to update it.",
            "warning",
        )
        return

    upload.save(destination)
    flash(f"{filename} has been saved.", "success")


@admin_bp.route("/photos/delete", methods=["POST"])
@auth.login_required
def delete_photo():
    filename = secure_filename(request.form.get("filename", ""))
    path = os.path.join(_images_dir(), filename)
    if filename and os.path.isfile(path):
        os.remove(path)
        flash(f"{filename} has been deleted.", "success")
    else:
        flash("That photo could not be found.", "danger")
    return redirect(url_for("admin.photos"))
