export LEGO_TEST_LOGFILE := "tests.log"

test-fast *args:
    python manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

test *args:
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test

serve-develop:
    python manage.py runserver --nostatic

alias s := serve-develop

serve $LEGO_DEBUG="0":
    gunicorn project.asgi:application

db:
    docker run -d --rm --name pg_lego -p 5433:5432 --env POSTGRES_PASSWORD=devpgcontainer postgres:15

psql:
    docker exec -it --user postgres pg_lego psql
