export LEGO_TEST_LOGFILE := "tests.log"

test-fast *args:
    python manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser {{args}} lego

alias f := test-fast

test *args:
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 {{args}} lego
    coverage report --show-missing
    coverage html

alias t := test
