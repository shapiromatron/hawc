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

In general, for configurable parameters, we use environment variables and corresponding settings in the `hawc.main.settings.staging`_ module. If you need to configure something that's hard-coded, we're happy to modify the settings; feel free to contact us.

.. _`hawc.main.settings.staging`: https://github.com/shapiromatron/hawc/blob/main/hawc/main/settings/staging.py

Assessment creation & configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The django setting ``ANYONE_CAN_CREATE_ASSESSMENTS`` determines if anyone can create assessments, or if the ability to allow users to create assessments are controlled by system administrators. To change in staging/production, set the environment variable ``HAWC_ANYONE_CAN_CREATE_ASSESSMENTS`` to "True" or "False" (default "True").

If anyone cannot create assessments, either superusers or users assigned to the group named ``can-create-assessments`` are the only allowed to create assessments; if that group access is removed then assessment creation is also revoked.

- ``HAWC_SESSION_DURATION`` [int, default 604800 seconds or 1 week]. The length of a HAWC user-session. After this duration is exceeded, the user must login for a new session.

The django setting `PM_CAN_MAKE_PUBLIC` determines if project managers for an assessment have the ability to make an assessment public (and editable) on the HAWC website. The default behavior (True) allows this behavior. If set to False, only administrators make assessments public. To change in staging/production, set the environment variable ``HAWC_PM_CAN_MAKE_PUBLIC`` to "True" or "False" (default "True").
