#!/bin/sh

LOGFILE="$LOGS_PATH/celery.log"

exec /usr/local/bin/celery worker \
    --app=hawc \
    --loglevel=INFO \
    --logfile=$LOGFILE \
    --soft-time-limit=90 \
    --time-limit=120
