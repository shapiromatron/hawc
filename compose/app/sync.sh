#!/bin/bash

set -xe

manage clear_cache
manage clearsessions
manage collectstatic --noinput
manage migrate --noinput

if [[ $HAWC_LOAD_TEST_DB == "2" ]]; then
    echo "loading fixture database..."
    manage load_test_db
elif [[ $HAWC_LOAD_TEST_DB == "1" ]]; then
    echo "loading fixture database (if empty)..."
    manage load_test_db --ifempty
else
    echo "not modifying database..."
fi

# drop/rebuild materialized views
manage recreate_views

# succcessful exit for healthchecks
exit 0
