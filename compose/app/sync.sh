#!/bin/bash

set -xe

manage.py migrate --noinput
manage.py clear_cache
manage.py collectstatic --noinput

if [[ $HAWC_LOAD_TEST_DB == "True" ]]; then
    echo "loading test database..."
    manage.py load_test_db --ifempty
fi

# succcessful exit for healthchecks
exit 0
