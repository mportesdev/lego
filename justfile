test-fast:
    python manage.py test --keepdb --failfast --verbosity=2 --duration=10 --exclude-tag=write-db --exclude-tag=login --exclude-tag=browser lego

test:
    python -Wa -m coverage run manage.py test --noinput --shuffle --verbosity=2 --duration=10 lego
    coverage report --show-missing
    coverage html
