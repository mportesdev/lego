export LEGO_TEST_LOGFILE := "tests.log"

test-fast *args: db-health
    python -Wd manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

test *args: db-health
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test

serve-develop: db-health
    python manage.py runserver --nostatic

alias s := serve-develop

serve $LEGO_DEBUG="0": db-health
    gunicorn project.asgi:application

db-up:
    docker run -d --rm --name pg_lego -p 5433:5432 --env POSTGRES_PASSWORD=pglego postgres:16

db-down:
    docker stop pg_lego

db-health:
    docker exec -it --user postgres pg_lego pg_isready

db-bash: db-health
    docker exec -it --user postgres pg_lego bash

tasks: db-health
    python manage.py db_worker --verbosity=2

reinstall:
    pip install --upgrade pip
    pip install --force-reinstall -r requirements.txt -r test-requirements.txt
