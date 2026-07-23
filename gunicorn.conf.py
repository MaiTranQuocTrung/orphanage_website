"""Gunicorn configuration for the Tuệ Quang Shelter website.

Usage:
    gunicorn -c gunicorn.conf.py wsgi:app

Gunicorn listens only on localhost; Nginx sits in front as a reverse proxy
and serves static files. See DEPLOYMENT.md for the full setup.
"""

import multiprocessing
import os

# Bind to localhost only — Nginx proxies public traffic to this address.
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")

# A common formula: (2 x CPU cores) + 1. Override with GUNICORN_WORKERS.
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

worker_class = "sync"
timeout = 60
graceful_timeout = 30
keepalive = 5

# Log to stdout/stderr so systemd/journald captures them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

proc_name = "tuequang"
