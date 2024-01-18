#!/bin/bash

# stop on errors
set -e

# we might run into trouble when using the default `postgres` user, e.g. when dropping the postgres
# database in restore.sh. Check that something else is used here
if [ "$POSTGRES_USER" == "postgres" ]
then
    echo "creating a backup as the postgres user is not supported, make sure to set the POSTGRES_USER environment variable"
    exit 1
fi

# export the postgres password so that subsequent commands don't ask for it
export PGPASSWORD=$POSTGRES_PASSWORD

echo "creating backup"
echo "---------------"

mkdir -p /app/data/backups
FILENAME="hawc-$(date +"%Y-%m-%dT%H_%M").sql.gz"
pg_dump -U $POSTGRES_USER | gzip > /app/data/backups/$FILENAME

echo "successfully created backup $FILENAME"
