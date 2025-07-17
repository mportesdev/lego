export LEGO_TEST_LOGFILE := "tests.log"

test-fast *args: db-up
    python manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

test *args: db-up
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test

serve-develop: db-up
    python manage.py runserver --nostatic

alias s := serve-develop

serve $LEGO_DEBUG="0": db-up
    gunicorn project.asgi:application

db-start:
    docker run -d --rm --name pg_lego -p 5433:5432 --env POSTGRES_PASSWORD=devpgcontainer postgres:15

db-up:
    docker inspect pg_lego | jq -e '.[0].State.Status == "running"'
    docker exec -it --user postgres pg_lego pg_isready

psql: db-up
    docker exec -it --user postgres pg_lego psql

tasks: db-up
    python manage.py db_worker --verbosity=2

reinstall:
    pip install --force-reinstall -r requirements.txt -r test-requirements.txt
