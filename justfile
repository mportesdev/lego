test-fast *args: dbhealth
    python -Wd manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

[env("LEGO_TEST_LOGFILE", "tests.log")]
test *args: dbhealth
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test

serve-develop: dbhealth
    python manage.py runserver --nostatic

alias s := serve-develop

[env("LEGO_DEBUG", "0")]
serve: dbhealth
    gunicorn project.asgi:application

dbup:
    docker run -d --rm --name pg_lego -p 5433:5432 --env POSTGRES_PASSWORD=pglego postgres:16

dbdown:
    docker stop pg_lego

dbhealth:
    docker exec -it --user postgres pg_lego pg_isready

alias dbh := dbhealth

dbsh: dbhealth
    docker exec -it --user postgres pg_lego bash

tasks: dbhealth
    python manage.py db_worker --verbosity=2

reinstall:
    pip install --upgrade pip
    pip install --force-reinstall -r requirements.txt -r test-requirements.txt
