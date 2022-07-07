FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

RUN groupadd -g 555 -r app && \
    useradd -u 555 -r -g app app

COPY ./compose/app/wait-for.sh /app/bin/wait-for.sh
COPY ./compose/app/sync.sh /app/bin/sync.sh
COPY ./compose/app/web.sh /app/bin/web.sh
COPY ./compose/app/workers.sh /app/bin/workers.sh
COPY ./compose/app/cron.sh /app/bin/cron.sh
COPY ./vendor/bmds-0.11.0.tar.gz /app/build/vendor/bmds-0.11.0.tar.gz

# used in some dev/staging environments
COPY ./tests/data/fixtures/db.yaml /app/test-db-fixture.yaml

# security updates
# https://pythonspeed.com/articles/system-packages-docker/
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends netcat git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    \
    mkdir -p /app/logs

COPY ./requirements /app/build/requirements
COPY ./dist /app/build/dist

WORKDIR /app/build
RUN pip install -U pip && \
    pip install -r /app/build/requirements/production.txt --no-cache-dir && \
    rm -rf /app/build && \
    chown -R app:app /app

WORKDIR /app
USER app
