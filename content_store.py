"""Storage for content edited through the admin area.

Everything the shelter staff can change is kept in a single JSON file inside
Flask's instance folder, layered *on top of* the content that ships in the
code. The code stays the source of defaults; the store only holds what has
actually been edited. That way an empty store means "the site as shipped",
and deleting the file is a complete reset.

Shape of the file::

    {
      "text": {"en": {"<source string>": "<replacement>"}, "vi": {...}},
      "collections": {"events": [...], "stories": [...], "council": [...]}
    }
"""

import json
import os
import tempfile
import threading

_store_path = None
_write_lock = threading.Lock()

# Parsed copy of the file plus the mtime/size it was read from, so repeated
# requests do not re-parse JSON that has not changed.
_cache = {"stamp": None, "data": None}

_EMPTY = {"text": {}, "collections": {}}


def init_app(app):
    """Point the store at <instance>/content.json and make sure it exists."""
    global _store_path
    os.makedirs(app.instance_path, exist_ok=True)
    _store_path = os.path.join(app.instance_path, "content.json")
    app.config.setdefault("CONTENT_STORE_PATH", _store_path)


def get_path():
    return _store_path


def _stamp():
    try:
        info = os.stat(_store_path)
    except (OSError, TypeError):
        return None
    return (info.st_mtime_ns, info.st_size)


def _read_file():
    stamp = _stamp()
    if stamp is None:
        return json.loads(json.dumps(_EMPTY))
    if _cache["stamp"] == stamp and _cache["data"] is not None:
        return _cache["data"]
    try:
        with open(_store_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        # A corrupt or half-written file must never take the public site down.
        return json.loads(json.dumps(_EMPTY))
    data.setdefault("text", {})
    data.setdefault("collections", {})
    _cache["stamp"] = stamp
    _cache["data"] = data
    return data


def load():
    """Return the whole store, cached for the duration of a request.

    translate() calls this for every string on a page, so the per-request
    cache keeps it to at most one stat() per request.
    """
    try:
        from flask import g, has_app_context

        if has_app_context():
            cached = getattr(g, "_content_store", None)
            if cached is None:
                cached = _read_file()
                g._content_store = cached
            return cached
    except (ImportError, RuntimeError):
        pass
    return _read_file()


def _save(data):
    """Write the store atomically so readers never see a partial file."""
    with _write_lock:
        directory = os.path.dirname(_store_path)
        os.makedirs(directory, exist_ok=True)
        handle, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(temp_path, _store_path)
        except BaseException:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    _cache["stamp"] = None
    _cache["data"] = None
    try:
        from flask import g, has_app_context

        if has_app_context() and hasattr(g, "_content_store"):
            del g._content_store
    except (ImportError, RuntimeError):
        pass


# ---------------------------------------------------------------- text edits

def get_text(lang):
    """Edited strings for one language, keyed by the original English text."""
    return load().get("text", {}).get(lang, {})


def set_texts(lang, edits):
    """Apply a batch of edits. An empty value clears the override."""
    data = load()
    texts = data.setdefault("text", {}).setdefault(lang, {})
    changed = False
    for source, value in edits.items():
        value = (value or "").strip()
        if value:
            if texts.get(source) != value:
                texts[source] = value
                changed = True
        elif source in texts:
            del texts[source]
            changed = True
    if changed:
        _save(data)
    return changed


def clear_texts(sources):
    """Drop overrides for the given source strings in every language."""
    data = load()
    changed = False
    for lang_texts in data.get("text", {}).values():
        for source in sources:
            if source in lang_texts:
                del lang_texts[source]
                changed = True
    if changed:
        _save(data)
    return changed


# ---------------------------------------------------------- list collections

def get_collection(name, default):
    """Return an edited collection, or the default shipped in the code."""
    items = load().get("collections", {}).get(name)
    if items is None:
        return default
    return items


def save_collection(name, items):
    data = load()
    data.setdefault("collections", {})[name] = items
    _save(data)


def reset_collection(name):
    data = load()
    if name in data.get("collections", {}):
        del data["collections"][name]
        _save(data)
        return True
    return False
