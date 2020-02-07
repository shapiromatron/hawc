#!/bin/bash

set -e
cmd="$@"

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_USER

function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_USER", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="postgres")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}


# ensure we can connect to redis client;
# requires REDIS_CONNECTION_STRING environment variable
function redis_ready(){
python << END
import sys
import redis
try:
    client = redis.StrictRedis.from_url("$REDIS_CONNECTION_STRING")
    client.ping()
except redis.exceptions.ConnectionError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

until redis_ready; do
    >&2 echo "Redis is unavailable - sleeping"
    sleep 1
done

>&2 echo "Postgres and Redis are up - continuing..."
exec $cmd
