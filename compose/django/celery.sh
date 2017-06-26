#!/bin/sh

LOGFILE="$LOGS_PATH/celery.log"

# wait for migrations
sleep 10

exec /usr/local/bin/celery worker \
    --app=hawc \
    --loglevel=INFO \
    --logfile=$LOGFILE \
    --soft-time-limit=90 \
    --time-limit=120
