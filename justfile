export LEGO_TEST_LOGFILE := "tests.log"

test-fast:
    python manage.py test --keepdb --failfast --verbosity=2 --durations=10 --exclude-tag=browser lego

test:
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --durations=10 lego
    coverage report --show-missing
    coverage html
