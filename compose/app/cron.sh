#!/bin/bash

set -xe

# Run the django-crontask scheduler
exec python manage.py crontask
