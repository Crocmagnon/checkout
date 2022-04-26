#!/bin/bash
set -eux
python manage.py migrate --noinput
inv compilemessages
gunicorn checkout.wsgi -b 0.0.0.0:8000 --log-file -
