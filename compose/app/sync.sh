#!/bin/bash

set -xe

manage.py clear_cache
manage.py clearsessions
manage.py collectstatic --noinput
manage.py migrate --noinput

if [[ $HAWC_LOAD_TEST_DB == "2" ]]; then
    echo "loading fixture database..."
    manage.py load_test_db
elif [[ $HAWC_LOAD_TEST_DB == "1" ]]; then
    echo "loading fixture database (if empty)..."
    manage.py load_test_db --ifempty
else
    echo "not modifying database..."
fi

# drop/rebuild materialized views
manage.py recreate_views

# succcessful exit for healthchecks
exit 0
