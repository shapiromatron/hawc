#!/bin/bash

set -xe

/usr/local/bin/granian \
    --interface wsgi \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 3 \
    --workers-lifetime 3600 \
    --respawn-interval 60 \
    --access-log \
    --respawn-failed-workers \
    hawc.main.wsgi:application
