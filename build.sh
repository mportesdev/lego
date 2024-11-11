#!/usr/bin/env bash

set -eu

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py shell -c "$(cat check_superuser.py)"
