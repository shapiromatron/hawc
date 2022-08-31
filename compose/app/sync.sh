#!/bin/bash

set -xe

hawc clear_cache
hawc clearsessions
hawc collectstatic --noinput
hawc migrate --noinput

if [[ $HAWC_LOAD_TEST_DB == "2" ]]; then
    echo "loading fixture database..."
    hawc load_test_db
elif [[ $HAWC_LOAD_TEST_DB == "1" ]]; then
    echo "loading fixture database (if empty)..."
    hawc load_test_db --ifempty
else
    echo "not modifying database..."
fi

# drop/rebuild materialized views
hawc recreate_views

# succcessful exit for healthchecks
exit 0
