#!/bin/sh
set -e
cmd="$@"

>&2 echo "Waiting for django application ..."
/wait-for.sh django:5000 -t 30 -q
>&2 echo "Django application up  - continuing..."

exec $cmd
