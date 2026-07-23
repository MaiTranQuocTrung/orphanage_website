# Deployment (Gunicorn + Nginx)

The site runs as a WSGI app served by **Gunicorn**, with **Nginx** in front as a
reverse proxy and static-file server.

```
Internet ──▶ Nginx (port 80/443) ──▶ Gunicorn (127.0.0.1:8000) ──▶ Flask app
                     │
                     └─ serves /static/ directly
```

Files in this repo:

| File | Purpose |
|------|---------|
| `wsgi.py` | WSGI entry point (`wsgi:app`) |
| `gunicorn.conf.py` | Gunicorn settings (bind, workers, logging) |
| `deploy/nginx/tuequang.conf` | Nginx server block |
| `deploy/tuequang.service` | systemd unit to keep Gunicorn running |

---

## 1. Production deployment (Ubuntu/Debian server)

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx

# 2. Get the code
sudo git clone <repo-url> /opt/orphanage_website
cd /opt/orphanage_website

# 3. Create a virtualenv and install dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 4. Configure environment (email + secret key)
cp .env.example .env      # then edit .env and set SECRET_KEY, MAIL_* etc.

# 5. Install and start the Gunicorn service
sudo cp deploy/tuequang.service /etc/systemd/system/tuequang.service
sudo systemctl daemon-reload
sudo systemctl enable --now tuequang
sudo systemctl status tuequang        # verify it is running

# 6. Configure Nginx
#    Edit deploy/nginx/tuequang.conf first: set server_name and the
#    /static/ alias to /opt/orphanage_website/static/
sudo cp deploy/nginx/tuequang.conf /etc/nginx/sites-available/tuequang
sudo ln -s /etc/nginx/sites-available/tuequang /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

The site is now reachable at `http://<server-ip>/`.

### HTTPS (optional, recommended)

Once a domain points at the server:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 2. Local testing (no domain, no server)

Gunicorn is Unix-only and does **not** run on native Windows. Test using one of:

### Option A — Just Gunicorn (Linux / macOS / WSL)

```bash
pip install -r requirements.txt
gunicorn -c gunicorn.conf.py wsgi:app
# open http://127.0.0.1:8000
```

### Option B — Full Gunicorn + Nginx stack (Linux / WSL)

```bash
# start the app
gunicorn -c gunicorn.conf.py wsgi:app &

# point Nginx at it (uses the config in this repo, with the static path
# and listen port adjusted for local testing), then:
curl -I http://127.0.0.1:8080/
```

On **Windows**, run the above inside **WSL** (`wsl`) — the project is available
there at `/mnt/c/Users/<you>/orphanage_website`. Native Windows users who want a
pure-Windows WSGI server can use `waitress` instead of Gunicorn, but production
should use Gunicorn + Nginx on Linux.
