#!/bin/bash

set -xe

# Run the django-tasks database worker
exec python manage.py db_worker
