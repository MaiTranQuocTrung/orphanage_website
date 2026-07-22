# Tuệ Quang Children — Shelter Website

A Flask-based website for the Tuệ Quang Children orphanage/shelter, built with Jinja2 templates and Bootstrap 5.

## Project Structure

```
orphanage_website/
├── app.py                 # Flask application entry point
├── requirements.txt
├── data/
│   └── content.py         # Sample events, stories, council & staff data
├── routes/
│   ├── home.py            # Home page
│   ├── about.py           # About Us pages
│   ├── children.py        # Tuệ Quang Children pages
│   ├── policies.py        # Shelter policy pages
│   ├── events.py          # Events & Stories
│   └── support.py         # Registration forms
├── templates/             # Jinja2 HTML templates
└── static/
    ├── css/style.css
    └── js/main.js
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Pages

| Section | Routes |
|---------|--------|
| Home | `/` |
| About Us | `/about/history`, `/about/vision`, `/about/council`, `/about/org-chart` |
| Tuệ Quang Children | `/children/beneficiaries`, `/children/intake` |
| Shelter Policies | `/policies/rules`, `/policies/visitor`, `/policies/volunteer`, `/policies/child-protection` |
| Events & Stories | `/events/`, `/events/stories` |
| Support | `/support/volunteer`, `/support/sponsorship` |

## Notes

- Stock images are loaded from Unsplash CDN.
- Registration forms show a confirmation flash message (no backend persistence yet).
- Founding Council photos open a modal with member profiles on click.
