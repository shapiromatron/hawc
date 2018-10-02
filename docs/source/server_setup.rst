Server setup
============

Minimum hardware requirements:

- Linux OS (ex: Ubuntu 16.04, CentOS, or RHEL)
- 2 GB RAM (4 GB recommended)
- 2 processors (4-8 recommended)
- 40 GB HD space (120 GB recommended)

Software requirements:

- `docker`_ & `docker-compose`_
- `fabric`_ scripts are currently used for deployment (not in github repository)

For more details, see the `docker-compose.yml`_ file in the HAWC source code.

.. _`docker`: https://docs.docker.com/
.. _`docker-compose`: https://docs.docker.com/compose/
.. _`fabric`: http://www.fabfile.org/
.. _`docker-compose.yml`: https://github.com/shapiromatron/hawc/blob/master/docker-compose.yml


Required environment variables
------------------------------

The following environment variables are required for running in production;
please specify in the docker-compose `.env` file (example secrets below):

.. code-block:: bash

    # postgres
    POSTGRES_USER=myDbUser
    POSTGRES_PASSWORD=myDbPassword
    USE_DOCKER=yes

    # django; same as postgres
    DJANGO_DB_USER=myDbUser
    DJANGO_DB_NAME=hawc
    DJANGO_DB_HOST=postgres
    DJANGO_DB_PW=myDbPassword

    # django
    LOGS_PATH=/app/logs
    DJANGO_SETTINGS_MODULE=hawc.settings.production
    DJANGO_ALLOWED_HOSTS=hawcproject.org
    DJANGO_SECRET_KEY=myBigSecretKey
    DJANGO_ADMIN_EMAILS=johnny@appleseed.com|tommy@appleseed.com
    DJANGO_ADMIN_NAMES=Johnny Appleseed|Tommy Appleseed
    DJANGO_CACHE_LOCATION=redis://redis:6379/0
    DJANGO_BROKER_URL=redis://redis:6379/1
    DJANGO_CELERY_RESULT_BACKEND=redis://redis:6379/2
    CHEMSPIDER_TOKEN=myChemspiderToken
    PHANTOMJS_PATH=/usr/local/bin/phantomjs
    PUBMED_EMAIL=myEmail@email.com

    # Enum; one of {"PRIME", "EPA"}
    HAWC_FLAVOR=PRIME

    # email (use these settings if using SMTP)
    DJANGO_EMAIL_BACKEND=SMTP
    EMAIL_HOST=smtpHost
    EMAIL_HOST_USER=smtpHostUsername
    EMAIL_HOST_PASSWORD=smtpHostPassword
    EMAIL_PORT=smtpPortNumber
    EMAIL_USE_SSL=[True or False]

    # email (use these settings if using mailgun)
    DJANGO_EMAIL_BACKEND=MAILGUN
    MAILGUN_ACCESS_KEY=myMailgunAccessKey
    MAILGUN_SERVER_NAME=myMailgunServerName

    # required if using BMDS
    BMDS_SUBMISSION_URL = 'https://bmds-server/api/dfile/'
    BMDS_TOKEN = 'mysecrettoken'

    # ensure redis is running
    REDIS_CONNECTION_STRING=redis://redis:6379/0

Other required files are:

- TTF fonts (place in ``compose/django/fonts``)
    - Arial, HelveticaNeue, Times New Roman
- nginx configuration (place in ``compose/nginx/conf/nginx.conf``)
- nginx ssl certificates (place in ``compose/nginx/ssl``)

Deploying:
----------

To deploy, build and run all docker containers. Currently a javascript
bundle is built locally on the development server and then pushed to production.
Here is an example `fabric`_ script for doing so:

.. code-block:: python

    from fabric.api import task, local, lcd, cd, run, put


    @task
    def update():

        with lcd('/local/hawc/project'):
            local('npm run build')
            put(
                os.path.join('/local/hawc/project/webpack-stats.json'),
                '/apps/hawc/project',
                mode=0o644
            )
            put(
                os.path.join(/local/hawc/project/static/bundles/*'),
                '/remote/hawc/project/static/bundles/',
                mode=0o644
            )

        with cd('/remote/hawc'):
            run('git log -1 --format=%H > /remote/hawc/project/.gitcommit')
            run('docker-compose build django')
            run('docker-compose up --no-deps -d django')
