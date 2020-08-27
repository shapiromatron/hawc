#!/bin/sh
set -e
cmd="$@"

>&2 echo "Waiting for Postgres and Redis ..."
/app/bin/wait-for.sh redis:6379 -t 30 -q
/app/bin/wait-for.sh postgres:5432 -t 30 -q
>&2 echo "Postgres and Redis are up - continuing..."

exec $cmd
