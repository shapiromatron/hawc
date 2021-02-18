FROM python:3.6.13

ENV PYTHONUNBUFFERED 1

RUN groupadd -g 555 -r django && \
    useradd -u 555 -r -g django django

COPY ./compose/django/wait-for.sh /app/bin/wait-for.sh
COPY ./compose/django/sync.sh /app/bin/sync.sh
COPY ./compose/django/web.sh /app/bin/web.sh
COPY ./compose/django/workers.sh /app/bin/workers.sh
COPY ./compose/django/cron.sh /app/bin/cron.sh
COPY ./compose/django/phantomjs_openssh.conf /app/phantomjs_openssh.conf
COPY ./compose/django/fonts /usr/share/fonts/truetype/django
COPY ./vendor/phantomjs-2.1.1-linux-x86_64.tar.bz2 /phantomjs.tar.bz2

RUN apt-get update && \
    apt-get install -y netcat fonts-liberation && \
    rm -rf /var/lib/apt/lists/* && \
    fc-cache -fv && \
    su django -c "fc-cache -fvs" && \
    \
    tar -xvf /phantomjs.tar.bz2 phantomjs-2.1.1-linux-x86_64/bin/phantomjs -C /usr/local/bin && \
    rm /phantomjs.tar.bz2 && \
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
    chown -R django:django /app

USER django
