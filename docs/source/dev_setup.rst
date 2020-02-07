Development Setup
=================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- `Git`_
- `Python`_ ≥ 3.6
- `Node.js`_
- `Yarn`_
- `PostgreSQL`_ ≥ 9.4

.. _`Git`: https://git-scm.com/
.. _`Python`: https://www.python.org/
.. _`Node.js`: https://nodejs.org
.. _`Yarn`: https://yarnpkg.com/
.. _`PostgreSQL`: https://www.postgresql.org/


HAWC API
--------

Authenticated users can access HAWC REST APIs; below is an example script for use:

.. code-block:: python

    import requests

    session = requests.Session()
    login = requests.post(
        "https://hawcproject.org/user/api/token-auth/",
        json={"username": "me@me.com", "password": "keep-it-hidden"}
    )

    if login.status_code == 200:
        session.headers.update(Authorization=f"Token {login.json()['token']}")
    else:
        raise EnvironmentError("Authentication failed")

    session.get('https://hawcproject.org/ani/api/endpoint/?assessment_id=123').json()


HAWC developer environment setup
--------------------------------

Clone the repository and install all requirements into a virtual environment:

.. code-block:: bash

    # clone repository; we'll put in ~/dev but you can put anywhere
    mkdir -p ~/dev
    cd ~/dev
    git clone https://github.com/shapiromatron/hawc.git

    # create virtual environment and install requirements
    cd ~/dev/hawc
    python -m venv venv
    source ./venv/bin/activate
    $VIRTUAL_ENV/bin/pip install -r ./requirements/dev.txt

    # create a local settings file (optional; in case you want to change local settings)
    cp ./hawc/main/settings/local.example.py ./hawc/main/settings/local.py

Update the settings file with any changes you'd like to make for your local
development environment.

Current HAWC as two possible application "flavors", where the application is slightly
different depending on which flavor is selected. To change, modify the ``HAWC_FLAVOR``
variable in settings. Possible values include:

- PRIME (default application)
- EPA (EPA application)

You'll need to run both the python webserver and the node webserver to develop
HAWC; here are instructions how how to do both.

To run the python webserver:

.. code-block:: bash

    # create a PostgreSQL database
    createdb -E UTF-8 hawc

    # active python virtual environment and sync database schema with code
    cd ./project
    source ../venv/bin/activate
    python manage.py migrate
    python manage.py createcachetable

    # run development webserver
    python manage.py runserver

In a new terminal, run the node development webserver for javascript:

.. code-block:: bash

    # navigate to project folder
    cd ./project

    # install javascript dependencies
    yarn install

    # start node hot-reloading server
    npm start

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/


Using the bundled development environment
-----------------------------------------

For quicker development, HAWC includes a Makefile command which creates a `tmux`_
terminal for opening all required tabs for development. To execute, use the command::

    make dev

You can modify the tmux environment by creating a local copy::

    cp bin/dev.sh bin/dev.local.sh

.. _`tmux`: https://tmux.github.io/

Importing a database export:
----------------------------

To load a database export from the ``assessment_db_dump`` management command,
use the following arguments, if Postgres is available from the command-line::

    dropdb hawc         # if database already exists
    createdb hawc       # create new database
    psql –d hawc –f /path/to/export.sql

If Postgres tools are not available from the command-line, from a pqsl session::

    DROP DATABASE hawc;     --- drop database if exists
    CREATE DATABASE hawc;   --- create new database
    \c hawc                 --- open database
    \i /path/to/export.sql  --- load data into database

Building the test database:
---------------------------

A test database is loaded to run unit tests. The database may need to be periodically updated as new feature are added. To load, make edits, and export the test database:

.. code-block:: bash

    export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"

    # load existing test
    createdb hawc-test
    manage.py load_test_db

    # now make edits to the database using the GUI or via command line

    # export database
    manage.py dump_test_db


FAQ
---

- If your tests aren't working after the database has changed; try deleting and rebuilding the test database.
