FROM python:3.6.10

ENV PYTHONUNBUFFERED 1

RUN groupadd -g 555 -r django && \
    useradd -u 555 -r -g django django

COPY ./compose/django/entrypoint.sh /app/bin/entrypoint.sh
COPY ./compose/django/gunicorn.sh /app/bin/gunicorn.sh
COPY ./compose/django/celery.sh /app/bin/celery.sh
COPY ./compose/django/celerybeat.sh /app/bin/celerybeat.sh
COPY ./compose/django/supervisord.conf /app/bin/supervisord.conf
COPY ./compose/django/phantomjs_openssh.conf /app/phantomjs_openssh.conf
COPY ./compose/django/fonts /usr/share/fonts/truetype/django

# 1) install start-scripts
# 2) install phantomjs
# 3) install fonts
# 4) create logs path
RUN wget -O /phantomjs-2.1.1-linux-x86_64.tar.bz2 "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2" && \
    bzip2 -dc /phantomjs-2.1.1-linux-x86_64.tar.bz2 | tar xvf - && \
    mv /phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs && \
    rm -rf /phantomjs* && \
    \
    apt-get update && \
    apt-get install -y fonts-liberation && \
    rm -rf /var/lib/apt/lists/* && \
    fc-cache -fv && \
    su django -c "fc-cache -fvs" && \
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

ENTRYPOINT ["/app/bin/entrypoint.sh"]
