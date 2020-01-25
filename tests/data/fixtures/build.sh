#!/usr/bin/env bash
set -e

# to load:
# export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"
# manage.py flush --no-input
# manage.py loaddata tests/data/fixtures/db.yaml


# When created, fixtures aren't saved in any particular order,
# so many m2m issues may fail. Thus, we build this script to combine
# a single fixture in the correct order.
export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"

echo "migrate db"
manage.py migrate

echo "truncate test db"
manage.py flush --no-input

echo "running db load script"
manage.py shell < tests/data/fixtures/build.py

echo "writing exports"
# write first
manage.py dumpdata contenttypes --format=yaml --indent=2 > tests/data/fixtures/db.yaml

# append after
manage.py dumpdata myuser --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
manage.py dumpdata assessment --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
manage.py dumpdata lit --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
manage.py dumpdata study --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata animal --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata epi --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata invitro --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata riskofbias --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata mgmt --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata bmd --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
# manage.py dumpdata summary --format=yaml --indent=2 >> tests/data/fixtures/db.yaml
