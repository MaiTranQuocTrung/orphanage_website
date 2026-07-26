"""Lightweight internationalization helper.

Uses a gettext-style lookup: English is the source language and Vietnamese
translations are looked up by the original English string. Missing entries
fall back to the source text so nothing ever renders blank.
"""

from flask import session

import content_store
from translations import TRANSLATIONS

LANGUAGES = {
    "en": "English",
    "vi": "Tiếng Việt",
}
DEFAULT_LANGUAGE = "en"


def get_locale():
    lang = session.get("lang")
    if lang in LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE


def translate(text):
    """Render an English source string in the active language.

    Text edited through the admin area wins over both the shipped Vietnamese
    dictionary and the English source, so staff can reword any page without
    touching the templates.
    """
    if text is None:
        return text
    lang = get_locale()
    edited = content_store.get_text(lang)
    if text in edited:
        return edited[text]
    if lang == DEFAULT_LANGUAGE:
        return text
    return TRANSLATIONS.get(lang, {}).get(text, text)


def init_app(app):
    app.jinja_env.globals["_"] = translate

    @app.context_processor
    def inject_i18n():
        return {
            "current_lang": get_locale(),
            "languages": LANGUAGES,
        }
