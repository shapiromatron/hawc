#!/bin/bash

set -xe

exec /usr/local/bin/celery worker \
    --app=hawc.main.celery \
    --loglevel=INFO
