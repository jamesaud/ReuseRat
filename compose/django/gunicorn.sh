#!/bin/sh
python /app/manage.py collectstatic --noinput
python /app/manage.py makemigrations
python /app/manage.py migrate

/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app
