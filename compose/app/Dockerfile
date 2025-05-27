FROM quay.io/centos/centos:stream9-minimal

ENV PYTHON_VERSION=3.13 \
    PYTHONBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE=off \
    LANG=C.UTF-8

RUN groupadd -g 555 -r app && \
    useradd -u 555 -r -g app app

COPY ./compose/app/wait-for.sh /app/bin/wait-for.sh
COPY ./compose/app/sync.sh /app/bin/sync.sh
COPY ./compose/app/web.sh /app/bin/web.sh
COPY ./compose/app/workers.sh /app/bin/workers.sh
COPY ./compose/app/cron.sh /app/bin/cron.sh

# used in some dev/staging environments
COPY ./tests/data/fixtures/db.yaml /app/test-db-fixture.yaml

# security updates
# https://pythonspeed.com/articles/system-packages-docker/
RUN INSTALL_PKGS="python${PYTHON_VERSION} nc" && \
    VERIFY_PKGS="python${PYTHON_VERSION}" && \
    microdnf -y --setopt=tsflags=nodocs install $INSTALL_PKGS && \
    rpm -V $VERIFY_PKGS && \
    microdnf -y clean all --enablerepo='*' && \
    ln -s /usr/bin/"python${PYTHON_VERSION}" /usr/local/bin/python

COPY ./dist /app/build/dist

WORKDIR /app/build

RUN python -m ensurepip --upgrade && \
    python -m pip install -U pip && \
    python -m pip install "$(ls dist/hawc-*.whl | head -1)[prod]" && \
    mkdir -p /app/logs && \
    python -m pip uninstall -y pip setuptools && \
    rm -rf /app/build && \
    chown -R app:app /app

WORKDIR /app
USER app
