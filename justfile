test-fast *args: dbhealth
    python -Wd -m manage test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

[env("LEGO_TEST_LOGFILE", "tests.log")]
test *args: dbhealth check
    python -Wa -m coverage run -m manage test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test

[env("LEGO_TEST_FIREFOX_GUI", "1")]
test-gui *args: dbhealth
    python -m manage test --keepdb --verbosity=2 --durations=10 --tag=browser {{args}} lego

alias tg := test-gui

check:
    python -Wa -m manage makemigrations --check
    python -Wa -m manage migrate --check
    python -Wa -m manage check

serve-develop: dbhealth
    python -m manage runserver --nostatic

alias s := serve-develop

[env("LEGO_DEBUG", "0")]
serve: dbhealth
    gunicorn project.wsgi:application

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
    python -m manage db_worker --verbosity=2

reinstall:
    pip install --upgrade pip
    pip install --force-reinstall -r requirements.txt -r test-requirements.txt
