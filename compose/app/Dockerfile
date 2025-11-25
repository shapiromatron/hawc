FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    LANG=C.UTF-8

RUN groupadd -g 555 -r app && \
    useradd -u 555 -r -g app app

COPY ./compose/app/sync.sh /app/bin/sync.sh
COPY ./compose/app/web.sh /app/bin/web.sh
COPY ./compose/app/workers.sh /app/bin/workers.sh
COPY ./compose/app/cron.sh /app/bin/cron.sh

# used in some dev/staging environments
COPY ./tests/data/fixtures/db.yaml /app/test-db-fixture.yaml

# security updates
# https://pythonspeed.com/articles/system-packages-docker/
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY ./dist /app/build/dist

WORKDIR /app/build

RUN python -m pip install -U pip --root-user-action=ignore && \
    python -m pip install "$(ls -t dist/hawc-*.whl | head -1)[prod]" --no-cache-dir && \
    mkdir -p /app/logs && \
    python -m pip uninstall -y pip setuptools && \
    rm -rf /app/build && \
    chown -R app:app /app

WORKDIR /app
USER app
