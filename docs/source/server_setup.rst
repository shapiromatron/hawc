Server setup
============

Minimum hardware requirements:

- Linux OS (ex: Ubuntu 14.04, 16.04, CentOS, or RHEL)
- 2 GB RAM (4 GB recommended)
- 2 processors (4-8 recommended)
- 40 GB HD space (120 GB recommended)

Software requirements:

- Python 2.7
- Redis ≥ 2.8
- Git
- Nginx
- Node.js ≥ 4.5
- phantomjs ≥ 2.1.1
- PostgreSQL ≥ 9.4 (HAWC uses `jsonb`_)

Processes which should be always-on (currently using `supervisord`_):

- `Gunicorn`_ for running the django app
- `Celery`_ workers for running tasks
- Redis as a messaging and result broker for celery
- PostgreSQL for data persistence
- Nginx for web serving

`Fabric`_ scripts are currently used for deployment.


Required environment variables
------------------------------

The following environment variables will need to be set when running HAWC in
production.
 - For linux, you can set these values in ``$VIRTUAL_ENV/bin/activate``.
 - For Windows, you can set these values in ``activate.bat``, which should be located at ``%VIRTUAL_ENV%\Scripts\activate.bat``.


Example values are shown for each:

.. code-block:: bash

    #!/bin/bash

    # hawc settings
    export "DJANGO_ADMIN_NAMES=Johnny Appleseed|Tommy Appleseed"
    export "DJANGO_ADMIN_EMAILS=johnny@appleseed.com|tommy@appleseed.com"
    export "DJANGO_ALLOWED_HOSTS=hawc.mydomain.org|hawc.mydomain.com"
    export "DJANGO_SECRET_KEY=my-secret-key"

    # database settings
    export "DJANGO_DB_NAME=hawc"
    export "DJANGO_DB_USER=hawc"
    export "DJANGO_DB_PW=my-password"

    # email settings
    export "MAILGUN_ACCESS_KEY=my-secret-key"
    export "MAILGUN_SERVER_NAME=my.server.name"

    # caching and celery
    export "DJANGO_BROKER_URL=redis://localhost:6379/0"
    export "DJANGO_CELERY_RESULT_BACKEND=redis://localhost:6379/0"
    export "DJANGO_CACHE_SOCK=127.0.0.1:6379:1"

    # filesystem settings
    export "DJANGO_STATIC_DIRS=/path/to/hawc/project/static|/path/to/venv/lib/python2.7/site-packages/django/contrib/admin/static"
    export "LOGS_PATH=/path/to/logs/hawc"
    export "PHANTOMJS_PATH=/path/to/phantomjs"

    # external systems which hawc uses
    export "DJANGO_CHEMSPIDER_TOKEN=my-secret-key"
    export "PUBMED_EMAIL=johnny@appleseed.com"
    export "BMDS_HOST=http://bmds-server.mydomain.org"
    export "BMDS_PASSWORD=my-password"
    export "BMDS_USERNAME=my-username"

.. _`jsonb`: https://www.postgresql.org/docs/9.5/static/datatype-json.html
.. _`supervisord`: http://supervisord.org/
.. _`Gunicorn`: http://gunicorn.org/
.. _`Celery`: http://www.celeryproject.org/
.. _`Fabric`: http://www.fabfile.org/
