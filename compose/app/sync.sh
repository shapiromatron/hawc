#!/bin/bash

set -xe

if [[ $HAWC_LOAD_TEST_DB == "1" ]]; then
    echo "loading fixture database..."
    manage load_test_db
fi

manage clear_cache
manage clearsessions
manage collectstatic --noinput
manage migrate --noinput

# drop/rebuild materialized views
manage recreate_views

# successful exit for healthcheck
exit 0
