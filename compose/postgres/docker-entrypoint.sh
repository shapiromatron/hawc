#!/bin/bash

set -e

# do extra stuff after initial entry
if [[ "$POSTGRES_RECREATE_DB" == "1" ]]; then
    echo "Recreate database \"$POSTGRES_DB\""
    export PGPASSWORD="${PGPASSWORD:-$POSTGRES_PASSWORD}"
    dropdb --if-exists --username "$POSTGRES_USER" "$POSTGRES_DB"
    createdb --username "$POSTGRES_USER" "$POSTGRES_DB"
    unset PGPASSWORD
else
    echo "Reuse database \"$POSTGRES_DB\""
fi

# execute entrypoint as we normaly would
# https://github.com/docker-library/postgres/blob/master/docker-entrypoint.sh
exec docker-entrypoint.sh "$@"
