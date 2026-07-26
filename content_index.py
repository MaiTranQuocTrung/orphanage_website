"""Inventory of the editable text on every page.

Every visible string in the templates is wrapped in ``_("...")``, so the set
of editable strings can simply be read back out of the template files. This
means new copy added to a template shows up in the admin area automatically,
with no separate list to keep in sync.
"""

import os
import re

# _("text") or _('text'), tolerating escaped quotes inside the string.
_CALL_RE = re.compile(
    r"""_\(\s*(?P<quote>["'])(?P<text>(?:\\.|(?!(?P=quote))[^\\])*)(?P=quote)\s*\)""",
    re.S,
)

_TITLE_RE = re.compile(r"{%-?\s*block\s+title\s*-?%}(?P<body>.*?){%-?\s*endblock", re.S)

# Folders that are not part of the public site.
_SKIP_DIRS = {"admin"}

# Templates whose strings belong to another page (macros) or that need a
# friendlier name than their title block provides.
_SKIP_TEMPLATES = {"partials/page_header.html"}
_LABELS = {"base.html": "Site header & footer"}

# Where to preview a page after editing it.
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

# Rough reading order for the admin page list.
_ORDER = [
    "base.html",
    "home/index.html",
    "about/history.html",
    "about/vision.html",
    "governance/charter.html",
    "governance/organization.html",
    "children/beneficiaries.html",
    "children/intake.html",
    "children/child_rights.html",
    "policies/rules.html",
    "policies/visitor.html",
    "policies/volunteer_policy.html",
    "policies/child_protection.html",
    "events/events.html",
    "events/stories.html",
    "support/volunteer.html",
    "support/sponsorship.html",
]

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


def _strings_in(source, skip=()):
    """Unique source strings in template order, minus the page title."""
    seen = []
    for match in _CALL_RE.finditer(source):
        text = _unescape(match.group("text"))
        if text and text not in seen:
            seen.append(text)
    for text in skip:
        if text in seen:
            seen.remove(text)
    return seen


def _stamp(root):
    marks = []
    for key, full in _template_files(root):
        try:
            marks.append((key, os.stat(full).st_mtime_ns))
        except OSError:
            continue
    return tuple(sorted(marks))


def get_pages(root):
    """Return [{key, label, preview, strings}] for every editable page."""
    stamp = _stamp(root)
    if _cache["stamp"] == stamp and _cache["pages"] is not None:
        return _cache["pages"]

    pages = []
    for key, full in _template_files(root):
        try:
            with open(full, "r", encoding="utf-8") as handle:
                source = handle.read()
        except OSError:
            continue
        label = _label_for(key, source)
        title_match = _TITLE_RE.search(source)
        title_strings = ()
        if title_match:
            title_strings = tuple(
                _unescape(m.group("text")) for m in _CALL_RE.finditer(title_match.group("body"))
            )
        strings = _strings_in(source, skip=title_strings)
        if not strings:
            continue
        pages.append(
            {
                "key": key,
                "label": label,
                "preview": _PREVIEW.get(key),
                "strings": strings,
            }
        )

    order = {key: position for position, key in enumerate(_ORDER)}
    pages.sort(key=lambda page: (order.get(page["key"], len(_ORDER)), page["label"]))
    _cache["stamp"] = stamp
    _cache["pages"] = pages
    return pages


def get_page(root, key):
    for page in get_pages(root):
        if page["key"] == key:
            return page
    return None


def usage_counts(root):
    """How many pages each source string appears on."""
    counts = {}
    for page in get_pages(root):
        for text in page["strings"]:
            counts[text] = counts.get(text, 0) + 1
    return counts
