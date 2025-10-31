#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running migrations"
python manage.py makemigrations
python manage.py migrate --noinput

echo "==> Loading initial data"
python manage.py loaddata login/fixtures/social_apps.json || echo "No social_apps.json found."

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Build complete"
