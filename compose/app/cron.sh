#!/bin/bash

set -xe

# Run the APScheduler-based task scheduler
exec python manage.py run_scheduler
