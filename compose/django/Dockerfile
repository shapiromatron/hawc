FROM python:3.6.1

ENV PYTHONUNBUFFERED 1

RUN groupadd -r django && \
    useradd -r -g django django

COPY ./compose/django/entrypoint.sh /entrypoint.sh
COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/celery.sh /celery.sh
COPY ./compose/django/celerybeat.sh /celerybeat.sh
COPY ./compose/django/cull_backups.py /cull_backups.py
COPY ./compose/django/supervisord.conf /supervisord.conf
COPY ./compose/django/fonts /usr/share/fonts/truetype/django

# 1) install start-scripts
# 2) install supervisord on python2 (using pip)
# 3) install phantomjs
# 4) install fonts
# 3) create logs path
RUN chmod +x /entrypoint.sh && \
    chmod +x /gunicorn.sh && \
    chmod +x /celery.sh && \
    chmod +x /celerybeat.sh && \
    chmod +x /supervisord.conf && \
    chown django /entrypoint.sh && \
    chown django /gunicorn.sh && \
    chown django /celery.sh && \
    chown django /celerybeat.sh && \
    chown django /supervisord.conf && \
    \
    wget -O /get-pip.py "https://bootstrap.pypa.io/get-pip.py" && \
    python2.7 /get-pip.py --disable-pip-version-check --no-cache-dir && \
    pip2 install supervisor && \
    rm /get-pip.py && \
    \
    wget -O /phantomjs-2.1.1-linux-x86_64.tar.bz2 "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2" && \
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
RUN pip3 install \
        -r /requirements/production.txt \
        --no-cache-dir && \
    rm -rf /requirements

COPY ./project /app/project

RUN chown -R django /app

WORKDIR /app/project

ENTRYPOINT ["/entrypoint.sh"]
