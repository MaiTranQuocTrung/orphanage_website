# Tuệ Quang Children — Shelter Website

A Flask-based website for the Tuệ Quang Children orphanage/shelter, built with Jinja2 templates and Bootstrap 5.

## Project Structure

```
orphanage_website/
├── app.py                 # Flask application entry point
├── requirements.txt
├── auth.py                # Sign-in for the site editor
├── content_store.py       # Saved edits (instance/content.json)
├── content_index.py       # Finds the editable text in each template
├── site_content.py        # Events/stories/council after any edits
├── data/
│   └── content.py         # Sample events, stories, council & staff data
├── routes/
│   ├── home.py            # Home page
│   ├── about.py           # About Us pages
│   ├── children.py        # Tuệ Quang Children pages
│   ├── governance.py      # Charter & organization pages
│   ├── policies.py        # Shelter policy pages
│   ├── events.py          # Events & Stories
│   ├── support.py         # Registration forms
│   └── admin.py           # Site editor
├── tools/
│   └── hash_password.py   # Generates ADMIN_PASSWORD_HASH
├── templates/             # Jinja2 HTML templates
└── static/
    ├── css/style.css
    ├── css/admin.css
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

## Site Editor

Shelter staff can change the website's wording, lists, and photos from
[http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) — no code, no
redeploy. The editor is available in English and Vietnamese, and the language
switcher in its top bar works exactly like the one on the public site.

### Setting up the account

There is one editor account, configured through environment variables. Until
both a username and a password are set, every sign-in is refused, so a fresh
deployment is closed by default.

| Variable | Notes |
|----------|-------|
| `ADMIN_USERNAME` | The name used to sign in |
| `ADMIN_PASSWORD` | Plain password — simplest, fine for a local or trusted server |
| `ADMIN_PASSWORD_HASH` | Preferred. Wins over `ADMIN_PASSWORD` if both are set |
| `SECRET_KEY` | Signs the login cookie. Use a long random value in production |

To avoid keeping the real password on disk, generate a hash instead:

```bash
python tools/hash_password.py
```

Paste the printed `ADMIN_PASSWORD_HASH=...` line into `.env` and leave
`ADMIN_PASSWORD` blank. After five failed sign-ins an address is locked out for
15 minutes.

### What can be edited

- **Page text** — every heading, paragraph, and button on every page, in both
  languages. The list is read straight from the templates, so copy added later
  appears automatically.
- **Events, Stories of Love, Founding Council** — add, edit, reorder, and
  delete entries.
- **Images** — upload new photos, or replace an existing one. Replacing keeps
  the filename, so the new picture appears everywhere that image is used.

### How edits are stored

Edits are saved to `instance/content.json` and layered on top of the content
that ships in the code, which stays the source of the defaults. Text is keyed
by its original English wording, so nothing in the templates has to change.

That means:

- Every editor screen has a **Restore Original** button.
- Deleting `instance/content.json` resets the whole site to its shipped state.
- The folder is git-ignored, so edits made on the server are never in conflict
  with a deployment.

Back it up along with `static/img/` if you want to preserve staff edits.

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
| Site editor | `/admin` (sign-in required) |

## Notes

- Stock images are loaded from Unsplash CDN.
- Registration forms email submissions to the shelter and show a confirmation flash message.
- Founding Council photos open a modal with member profiles on click.
- `/about/council`, `/about/org-chart`, and the Events & Stories pages still work but are not in the top navigation; the homepage links to the events and stories pages.
