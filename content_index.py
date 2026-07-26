"""Inventory of the editable text on every page.

Every visible string in the templates is wrapped in ``_("...")``, so the set
of editable strings can simply be read back out of the template files. This
means new copy added to a template shows up in the editor automatically, with
no separate list to keep in sync.

Each string also gets a plain-language role — heading, paragraph, button —
worked out from the tag that surrounds it, so an editor can tell at a glance
which box matches which part of the page.
"""

import os
import re

# _("text") or _('text'), tolerating escaped quotes inside the string.
_CALL_RE = re.compile(
    r"""_\(\s*(?P<quote>["'])(?P<text>(?:\\.|(?!(?P=quote))[^\\])*)(?P=quote)\s*\)""",
    re.S,
)

_TITLE_RE = re.compile(r"{%-?\s*block\s+title\s*-?%}(?P<body>.*?){%-?\s*endblock", re.S)
_OPEN_TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b")
_ATTRIBUTE_RE = re.compile(r"""([a-zA-Z-]+)\s*=\s*["'][^"']*$""")

# Folders that are not part of the public site.
_SKIP_DIRS = {"admin"}

# Templates whose strings belong to another page (macros).
_SKIP_TEMPLATES = {"partials/page_header.html"}

# Markup that only signed-in staff ever see is not site content, so it is
# fenced off with {# editor-only:start #} ... {# editor-only:end #}.
_EDITOR_ONLY_RE = re.compile(
    r"{#\s*editor-only:start\s*#}.*?{#\s*editor-only:end\s*#}", re.S
)

_LABELS = {"base.html": "Menu & footer"}
_NOTES = {"base.html": "Appears on every page of the website."}

# Where each page lives on the public site.
_PREVIEW = {
    "home/index.html": "/",
    "about/history.html": "/about/history",
    "about/vision.html": "/about/vision",
    "about/council.html": "/about/council",
    "about/org_chart.html": "/about/org-chart",
    "governance/charter.html": "/governance/charter",
    "governance/organization.html": "/governance/organization",
    "children/beneficiaries.html": "/children/beneficiaries",
    "children/intake.html": "/children/intake",
    "children/child_rights.html": "/children/child-rights",
    "policies/rules.html": "/policies/rules",
    "policies/visitor.html": "/policies/visitor",
    "policies/volunteer_policy.html": "/policies/volunteer",
    "policies/child_protection.html": "/policies/child-protection",
    "events/events.html": "/events/",
    "events/stories.html": "/events/stories",
    "support/volunteer.html": "/support/volunteer",
    "support/sponsorship.html": "/support/sponsorship",
    "base.html": "/",
}

# The page list follows the website's own menu so editors recognise it.
_SECTIONS = [
    ("Every page", ["base.html"]),
    ("Home", ["home/index.html"]),
    ("About Us", ["about/history.html", "about/vision.html"]),
    (
        "Tuệ Quang Children",
        ["children/beneficiaries.html", "children/intake.html", "children/child_rights.html"],
    ),
    ("Governance", ["governance/charter.html", "governance/organization.html"]),
    (
        "Shelter Policies",
        [
            "policies/rules.html",
            "policies/visitor.html",
            "policies/volunteer_policy.html",
            "policies/child_protection.html",
        ],
    ),
    ("Events & Stories", ["events/events.html", "events/stories.html"]),
    ("Support the Shelter", ["support/volunteer.html", "support/sponsorship.html"]),
]

_OTHER_SECTION = "Not in the menu"

_TAG_ROLES = {
    "h1": "Heading",
    "h2": "Heading",
    "h3": "Heading",
    "h4": "Small heading",
    "h5": "Small heading",
    "h6": "Small heading",
    "p": "Paragraph",
    "li": "List item",
    "a": "Link",
    "button": "Button",
    "label": "Form label",
    "option": "Dropdown choice",
    "span": "Short text",
    "small": "Short text",
    "strong": "Short text",
    "em": "Short text",
    "td": "Table cell",
    "th": "Table heading",
    "figcaption": "Caption",
    "summary": "Short text",
}

_ATTRIBUTE_ROLES = {
    "placeholder": "Placeholder text",
    "alt": "Image description",
    "title": "Tooltip",
    "aria-label": "Accessibility label",
}

_cache = {"stamp": None, "pages": None}


def _unescape(raw):
    """Undo the backslash escapes Jinja would have processed."""
    out = []
    index = 0
    while index < len(raw):
        char = raw[index]
        if char == "\\" and index + 1 < len(raw):
            following = raw[index + 1]
            if following in ("'", '"', "\\"):
                out.append(following)
                index += 2
                continue
            if following == "n":
                out.append("\n")
                index += 2
                continue
        out.append(char)
        index += 1
    return "".join(out)


def _role_at(source, position):
    """Describe what the string at this position is, in plain language."""
    head = source[:position]

    # Page titles come from a macro call rather than a surrounding tag.
    last_expression = head.rfind("{{")
    if last_expression > head.rfind("}}"):
        expression = head[last_expression:]
        if "page_header(" in expression:
            return "Page title" if expression.count("_(") == 0 else "Page subtitle"

    last_open = head.rfind("<")
    if last_open > head.rfind(">"):
        attribute = _ATTRIBUTE_RE.search(head[last_open:])
        if attribute:
            return _ATTRIBUTE_ROLES.get(attribute.group(1).lower(), "Text")
        return "Text"

    tag = None
    for match in _OPEN_TAG_RE.finditer(head):
        tag = match.group(1).lower()
    return _TAG_ROLES.get(tag, "Text")


def _template_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            full = os.path.join(dirpath, name)
            key = os.path.relpath(full, root).replace(os.sep, "/")
            if key in _SKIP_TEMPLATES:
                continue
            yield key, full


def _label_for(key, source):
    if key in _LABELS:
        return _LABELS[key]
    match = _TITLE_RE.search(source)
    if match:
        strings = [_unescape(m.group("text")) for m in _CALL_RE.finditer(match.group("body"))]
        if strings:
            return strings[0]
    return key.rsplit("/", 1)[-1].replace("_", " ").replace(".html", "").title()


_VAGUE_ROLES = {"Text", "Browser tab title"}


def _entries_in(source):
    """Editable strings in page order, each with its role.

    A string used twice on a page — the browser tab title and the heading, say
    — is one editable box, described by the most specific of its roles.
    """
    title_match = _TITLE_RE.search(source)
    title_span = title_match.span("body") if title_match else (-1, -1)

    entries = []
    seen = {}
    for match in _CALL_RE.finditer(source):
        text = _unescape(match.group("text"))
        if not text:
            continue
        if title_span[0] <= match.start() < title_span[1]:
            role = "Browser tab title"
        else:
            role = _role_at(source, match.start())
        if text in seen:
            if seen[text]["role"] in _VAGUE_ROLES and role not in _VAGUE_ROLES:
                seen[text]["role"] = role
            continue
        entry = {"text": text, "role": role}
        seen[text] = entry
        entries.append(entry)
    return entries


def _stamp(root):
    marks = []
    for key, full in _template_files(root):
        try:
            marks.append((key, os.stat(full).st_mtime_ns))
        except OSError:
            continue
    return tuple(sorted(marks))


def get_pages(root):
    """Return [{key, label, note, preview, section, entries, strings}] per page."""
    stamp = _stamp(root)
    if _cache["stamp"] == stamp and _cache["pages"] is not None:
        return _cache["pages"]

    section_of = {}
    order = {}
    position = 0
    for section, keys in _SECTIONS:
        for key in keys:
            section_of[key] = section
            order[key] = position
            position += 1

    pages = []
    for key, full in _template_files(root):
        try:
            with open(full, "r", encoding="utf-8") as handle:
                source = handle.read()
        except OSError:
            continue
        source = _EDITOR_ONLY_RE.sub("", source)
        entries = _entries_in(source)
        if not entries:
            continue
        pages.append(
            {
                "key": key,
                "label": _label_for(key, source),
                "note": _NOTES.get(key),
                "preview": _PREVIEW.get(key),
                "section": section_of.get(key, _OTHER_SECTION),
                "entries": entries,
                "strings": [entry["text"] for entry in entries],
            }
        )

    pages.sort(key=lambda page: (order.get(page["key"], len(order)), page["label"]))
    _cache["stamp"] = stamp
    _cache["pages"] = pages
    return pages


def get_sections(root):
    """The pages grouped the same way the website's own menu is grouped."""
    grouped = []
    for page in get_pages(root):
        if not grouped or grouped[-1]["label"] != page["section"]:
            grouped.append({"label": page["section"], "pages": []})
        grouped[-1]["pages"].append(page)
    return grouped


def get_page(root, key):
    for page in get_pages(root):
        if page["key"] == key:
            return page
    return None


def key_for_path(root, path):
    """Which page is being shown at this URL, for the 'Edit this page' link."""
    if not path:
        return None
    normalised = path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else path
    for page in get_pages(root):
        preview = page["preview"]
        if page["key"] == "base.html" or not preview:
            continue
        if preview == normalised or preview.rstrip("/") == normalised.rstrip("/"):
            return page["key"]
    return None


def usage_counts(root):
    """How many pages each source string appears on."""
    counts = {}
    for page in get_pages(root):
        for text in page["strings"]:
            counts[text] = counts.get(text, 0) + 1
    return counts
