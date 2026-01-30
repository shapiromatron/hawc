#!/bin/bash

set -xe

exec python manage.py db_worker
