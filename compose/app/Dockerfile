FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

RUN groupadd -g 555 -r app && \
    useradd -u 555 -r -g app app

COPY ./compose/app/wait-for.sh /app/bin/wait-for.sh
COPY ./compose/app/sync.sh /app/bin/sync.sh
COPY ./compose/app/web.sh /app/bin/web.sh
COPY ./compose/app/workers.sh /app/bin/workers.sh
COPY ./compose/app/cron.sh /app/bin/cron.sh
COPY ./compose/app/phantomjs_openssh.conf /app/phantomjs_openssh.conf
COPY ./compose/app/fonts /usr/share/fonts/truetype/app
COPY ./vendor/phantomjs-2.1.1-linux-x86_64.tar.bz2 /phantomjs.tar.bz2

# used in some dev/staging environments
COPY ./tests/data/fixtures/db.yaml /app/test-db-fixture.yaml

RUN apt-get update && \
    apt-get install -y netcat fonts-liberation bzip2 fontconfig git && \
    rm -rf /var/lib/apt/lists/* && \
    fc-cache -fv && \
    su app -c "fc-cache -fvs" && \
    \
    tar -xvf /phantomjs.tar.bz2 phantomjs-2.1.1-linux-x86_64/bin/phantomjs && \
    mv /phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/ && \
    rm -rf /phantomjs* && \
    \
    mkdir -p /app/logs && \
    mkdir -p /app/public/media && \
    mkdir -p /app/public/media/bmds_plot

COPY ./requirements /requirements
RUN pip install -U pip && \
    pip install -r /requirements/production.txt --no-cache-dir && \
    rm -rf /requirements

WORKDIR /app

COPY ./dist/hawc.tar.gz /app/hawc.tar.gz
RUN tar -xf /app/hawc.tar.gz -C /app && \
    rm /app/hawc.tar.gz && \
    pip install -e . && \
    chown -R app:app /app

USER app
