#!/usr/bin/env bash

set -eu

python generate_key.py
echo -n $RENDER_EXTERNAL_HOSTNAME > .hosts

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py shell -c "$(cat check_superuser.py)"
