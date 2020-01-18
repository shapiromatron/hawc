#!/bin/sh

python manage.py migrate --noinput &> migrations.txt
python manage.py clear_cache
python manage.py collectstatic --noinput

LOGFILE="$LOGS_PATH/gunicorn.log"

# serve w/ gunicorn
/usr/local/bin/gunicorn main.wsgi \
    --bind 0.0.0.0:5000 \
    --chdir=/app/project \
    --timeout 300 \
    --workers 3 \
    --log-level info \
    --log-file $LOGFILE \
    --max-requests 750 \
    --max-requests-jitter 250
