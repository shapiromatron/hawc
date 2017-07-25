#!/bin/sh

LOGFILE="$LOGS_PATH/celerybeat.log"

# wait for migrations
sleep 10

exec /usr/local/bin/celery beat \
    --app=hawc \
    --loglevel=INFO \
    --logfile=$LOGFILE
