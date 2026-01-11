#!/bin/bash

set -xe

/usr/local/bin/granian \
    --interface wsgi \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 3 \
    --log-level info \
    --access-log \
    --respawn-failed-workers \
    hawc.main.wsgi:application
