#!/bin/bash

set -xe

manage.py migrate --noinput
manage.py clear_cache
manage.py collectstatic --noinput
