#!/usr/bin/env bash

set -eu

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py shell -c 'from django.contrib.auth.models import User; User.objects.get(username="admin")' || python manage.py createsuperuser --no-input --username=admin --email=""

python manage.py dumpdata lego > lego.json
python manage.py dumpdata auth.user > user.json
ln -s lego.log log.txt
ln -sr lego.json user.json log.txt staticfiles/
