"""The lists of content the site renders, after any admin edits.

Public routes read from here rather than importing the defaults directly, so
whatever staff save in the admin area is what visitors see. Until something is
edited these simply hand back the sample content from ``data/content.py``.
"""

import content_store
from data import EVENTS, FOUNDING_COUNCIL, STORIES

# Each collection describes its own edit form, so the admin templates stay
# generic and adding a field here is enough to expose it.
COLLECTIONS = {
    "events": {
        "label": "Events",
        "description": "Shown on the Events page and the homepage.",
        "default": EVENTS,
        "id_prefix": None,
        "title_field": "title",
        "fields": [
            {"name": "title", "label": "Title", "type": "text", "required": True},
            {"name": "date", "label": "Date", "type": "text"},
            {"name": "summary", "label": "Summary", "type": "textarea"},
            {"name": "image", "label": "Image", "type": "image"},
            {"name": "link", "label": "Link", "type": "text"},
        ],
    },
    "stories": {
        "label": "Stories of Love",
        "description": "Shown on the Stories page and the homepage.",
        "default": STORIES,
        "id_prefix": None,
        "title_field": "title",
        "fields": [
            {"name": "title", "label": "Title", "type": "text", "required": True},
            {"name": "date", "label": "Date", "type": "text"},
            {"name": "excerpt", "label": "Excerpt", "type": "textarea"},
            {"name": "image", "label": "Image", "type": "image"},
            {"name": "link", "label": "Link", "type": "text"},
        ],
    },
    "council": {
        "label": "Founding Council",
        "description": "Member photos and profiles.",
        "default": FOUNDING_COUNCIL,
        "id_prefix": "council-",
        "title_field": "name",
        "fields": [
            {"name": "name", "label": "Name", "type": "text", "required": True},
            {"name": "role", "label": "Role", "type": "text"},
            {"name": "photo", "label": "Photo", "type": "image"},
            {"name": "bio", "label": "Biography", "type": "textarea"},
        ],
    },
}


def get_items(name):
    config = COLLECTIONS[name]
    return content_store.get_collection(name, config["default"])


def save_items(name, items):
    content_store.save_collection(name, assign_ids(name, items))


def reset_items(name):
    return content_store.reset_collection(name)


def is_edited(name):
    return content_store.load().get("collections", {}).get(name) is not None


def assign_ids(name, items):
    """Give every entry a stable id, keeping the ones already assigned."""
    prefix = COLLECTIONS[name]["id_prefix"]
    used = {item.get("id") for item in items if item.get("id")}
    counter = 1
    result = []
    for item in items:
        entry = dict(item)
        if not entry.get("id"):
            while True:
                candidate = f"{prefix}{counter}" if prefix else counter
                counter += 1
                if candidate not in used:
                    break
            used.add(candidate)
            entry["id"] = candidate
        result.append(entry)
    return result


def get_events():
    return get_items("events")


def get_stories():
    return get_items("stories")


def get_council():
    return get_items("council")


def get_recent_events(limit=3):
    return get_events()[:limit]


def get_recent_stories(limit=3):
    return get_stories()[:limit]
