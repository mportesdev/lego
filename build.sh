#!/usr/bin/env bash

set -eu

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py shell -c 'from django.contrib.auth.models import User; User.objects.get(username="admin")' || python manage.py createsuperuser --no-input --username=admin --email=""

python manage.py dumpdata lego > staticfiles/dump.json
cp --force lego.log staticfiles/
