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

.. _`jsonb`: https://www.postgresql.org/docs/9.5/static/datatype-json.html
.. _`supervisord`: http://supervisord.org/
.. _`Gunicorn`: http://gunicorn.org/
.. _`Celery`: http://www.celeryproject.org/
.. _`Fabric`: http://www.fabfile.org/
