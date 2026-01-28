# https://hub.docker.com/hardened-images/catalog/dhi/python/images/
# https://hub.docker.com/hardened-images/catalog/dhi/uv/images/
FROM dhi.io/python:3.14-dev AS build-stage

COPY --from=dhi.io/uv:0 \
    /usr/local/bin/uv /usr/local/bin/uvx \
    /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=dist/,target=/app/dist \
    uv venv --no-managed-python && \
    source .venv/bin/activate && \
    uv pip install "$(ls -t dist/hawc-*.whl | head -1)[prod]"

# -----------------------------------------------------------------------------
FROM dhi.io/python:3.14 AS runtime-stage

COPY --from=build-stage /usr/bin/bash /usr/bin/bash
COPY --from=build-stage /app/.venv /app/.venv

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8

COPY ./compose/app/sync.sh /app/bin/sync.sh
COPY ./compose/app/web.sh /app/bin/web.sh
COPY ./compose/app/workers.sh /app/bin/workers.sh
COPY ./compose/app/cron.sh /app/bin/cron.sh
COPY ./tests/data/fixtures/db.yaml /app/test-db-fixture.yaml

USER app
WORKDIR /app
