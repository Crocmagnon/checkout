#!/bin/bash
set -eux
python manage.py migrate --noinput
python manage.py compilemessages -l en -l fr
gunicorn checkout.wsgi -b 0.0.0.0:8000 --log-file -
