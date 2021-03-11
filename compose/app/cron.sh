#!/bin/bash

set -xe

exec /usr/local/bin/celery beat \
    --app=hawc.main.celery \
    --loglevel=INFO
