#!/bin/bash

set -e

if [[ "$POSTGRES_RECREATE_DB" == "1" ]]; then
    echo "Recreate database \"$POSTGRES_DB\""
    dropdb --if-exists --username "$POSTGRES_USER" "$POSTGRES_DB"
    createdb --username "$POSTGRES_USER" "$POSTGRES_DB"
else
    echo "Reuse database \"$POSTGRES_DB\""
fi
