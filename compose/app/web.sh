#!/bin/bash

set -xe

/usr/local/bin/gunicorn hawc.main.wsgi \
    --bind 0.0.0.0:5000 \
    --chdir=/app \
    --timeout 300 \
    --workers 3 \
    --log-level info \
    --log-file - \
    --max-requests 750 \
    --max-requests-jitter 250
