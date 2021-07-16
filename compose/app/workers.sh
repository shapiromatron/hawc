#!/bin/bash

set -xe

exec /usr/local/bin/celery \
    --app=hawc.main.celery \
    worker \
    --loglevel=INFO
