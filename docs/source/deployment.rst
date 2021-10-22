Deployment
==========

Minimum hardware requirements:

- Linux
- 8 GB RAM (16 GB recommended)
- 2 processors (4-8 recommended)
- 100 GB HD space (SSD preferred)

Software requirements:

- docker and docker compose
- `fabric`_ is used for (semi) automated deployment; contact if you're interested and we can share ...

.. _fabric: http://www.fabfile.org/

HAWC has been deployed in the past on a bare-VM, using containers with docker-compose (recommended), on AWS with RDS, and in kubernetes. If you're looking for discussion deployment options, contact us!

Build and deploy
----------------

Build docker containers which can be deployed. These can be pushed to a container registry or
other approaches for sharing with the deployment target:

.. code-block:: bash

    # build containers (in the hawc development environment)
    source venv/bin/activate
    make build
    docker-compose -f compose/dc-build.yml --project-directory . build

To test-deploy the containers on your development computer:

.. code-block:: bash

    # go to a new directory
    cd ~/dev/temp
    mkdir -p hawc-deploy
    cd hawc-deploy

    # make shared volumes
    mkdir -p data/postgres/backups
    mkdir -p data/public
    mkdir -p data/private
    mkdir -p data/nginx

    # copy deployment settings
    cp ~/dev/hawc/compose/nginx/conf/nginx.example.conf ./data/nginx/nginx.conf
    cp ~/dev/hawc/compose/dc-deploy.yml ./docker-compose.yml
    cp ~/dev/hawc/compose/example.env ./.env

    # start containers, order is important
    # ... start the backend services
    docker-compose up -d redis postgres
    # ... one time filesystem/database changes
    docker-compose run --no-deps --rm sync
    # ... start applications
    docker-compose up -d web workers cron nginx

    # should be running, a few example commands for testing
    # check static files
    curl -I http://127.0.0.1:8000/static/css/hawc.css
    # check django request
    curl -I http://127.0.0.1:8000/user/login/
    docker-compose exec web manage.py createsuperuser
    docker-compose logs -f

    # shut down containers
    docker-compose down

The same approach can be done in production, except please harden the deployment :) .

Pex
---

Currently we're exploring the use of pex for bundling the entire python virtual environment into a single file, so it's available as a single environment that only requires a python runtime.  We expect that the containers may be modified in the future to use this pex artifact, but will requires further testing.

.. _`pex`: https://pypi.org/project/pex/

The following commands are used to generate and run the pex artifact:

.. code-block:: bash

    # build pex artifact
    make build-pex

    # activate environment variables ...

    # commands to run gunicorn WSGI server
    ./dist/hawc.pex run_gunicorn --bind 0.0.0.0:5000

    # commands to run workers and beat for scheduled tasks
    ./dist/hawc.pex run_celery --app=hawc.main.celery beat --loglevel=INFO
    ./dist/hawc.pex run_celery --app=hawc.main.celery worker --loglevel=INFO

Configuration
-------------

For configurable parameters, we use environment variables which are loaded in the application configuration at runtime.  See the example `configuration file`_ for a complete example. Many variables directly map to settings which are commonly used in django; refer to django documentation for these settings. Additional details on HAWC-specific variables are described below:

.. _`configuration file`: https://github.com/shapiromatron/hawc/blob/main/compose/example.env

- ``HAWC_ANYONE_CAN_CREATE_ASSESSMENTS`` [True/False; default True]. If true, anyone can create a new assessment. If false, or only those who are added to the ``can-create-assessments`` group by system administrators.
- ``HAWC_PM_CAN_MAKE_PUBLIC`` [True/False; default True].  If true, assessment project managers have the ability to make an assessment public (and editable) on the HAWC website. If False, only administrators can make assessments public.
- ``HAWC_INCLUDE_ADMIN`` [True/False, default True]. If true, the admin is included in the hawc deployment. If false, it's not included. In some deployments, the admin may be deployed separately with additional security.
