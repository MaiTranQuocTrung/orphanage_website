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

## Email Notifications

The Volunteer and Sponsorship forms email the submitted details to the shelter
(`tranlananh208c@gmail.com` by default). SMTP credentials are read from
environment variables so no secrets are stored in the repo. If they are not set,
the site still works and the submission is logged to the console instead.

| Variable | Example | Notes |
|----------|---------|-------|
| `MAIL_SERVER` | `smtp.gmail.com` | Required to send |
| `MAIL_PORT` | `587` | Defaults to `587` |
| `MAIL_USE_TLS` | `1` | Defaults to on |
| `MAIL_USERNAME` | `you@gmail.com` | Required to send |
| `MAIL_PASSWORD` | `app-password` | Gmail requires an [App Password](https://support.google.com/accounts/answer/185833) |
| `MAIL_SENDER` | `you@gmail.com` | Optional, defaults to `MAIL_USERNAME` |
| `MAIL_RECIPIENT` | `tranlananh208c@gmail.com` | Optional, this is the default |

Example (PowerShell):

```powershell
$env:MAIL_SERVER="smtp.gmail.com"; $env:MAIL_USERNAME="you@gmail.com"; $env:MAIL_PASSWORD="your-app-password"
python app.py
```

## Pages

| Section | Routes |
|---------|--------|
| Home | `/` |
| About Us | `/about/history`, `/about/vision` |
| Tuệ Quang Children | `/children/beneficiaries`, `/children/intake`, `/children/child-rights` |
| Governance | `/governance/charter`, `/governance/organization` |
| Shelter Policies | `/policies/rules`, `/policies/visitor`, `/policies/volunteer`, `/policies/child-protection` |
| Events & Stories | `/events/`, `/events/stories` |
| Support | `/support/volunteer`, `/support/sponsorship` |

## Notes

- Stock images are loaded from Unsplash CDN.
- Registration forms email submissions to the shelter and show a confirmation flash message.
- Founding Council photos open a modal with member profiles on click.
- `/about/council`, `/about/org-chart`, and the Events & Stories pages still work but are not in the top navigation; the homepage links to the events and stories pages.
