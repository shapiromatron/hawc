Deployment
==========

Minimum hardware requirements:

- Linux
- 8 GB RAM (16 GB recommended)
- 2 processors (4-8 recommended)
- 100 GB HD space (SSD preferred)

Software requirements:

- docker and docker compose
- `fabric`_ scripts are currently used for deployment, and are recommended for ease of use

Build and deploy
----------------

Build docker containers which can be deployed. These can be pushed to a container registry or
other approaches for sharing with the deployment target:

.. code-block:: bash

    # build containers (in the hawc development environment)
    source venv/bin/activate
    make build
    cp ./compose/example.env ./.env
    docker-compose -f compose/dc-build.yml --project-directory . build

To test-deploy the containers on your development computer:

.. code-block:: bash

    # go to a new directory
    cd ~/dev/temp
    mkdir -p hawc-deploy
    cd hawc-test-deploy

    # make shared volumes
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

Configuration
-------------

HAWC generally attempts to make reasonable defaults for configuration and setup, but there are a few variables which can be configured. These settings are configurable in the ``hawc.main.settings module``, and configurable parameters are generally changable via setting environment variables.

Assessment creation
~~~~~~~~~~~~~~~~~~~

The django setting ``ANYONE_CAN_CREATE_ASSESSMENTS`` determines if anyone can create assessments, or if the ability to allow users to create assessments are controlled by system administrators. To change in staging/production, set the environment variable ``HAWC_ANYONE_CAN_CREATE_ASSESSMENTS`` to "True" or "False" (default "True").

If anyone cannot create assessments, either superusers or users assigned to the group named ``can-create-assessments`` are the only allowed to create assessments; if that group access is removed then assessment creation is also revoked.
