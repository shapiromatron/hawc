Development setup
=================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- `Git`_
- `Python`_ ≥ 3.6
- `Node.js`_
- `Yarn`_
- `PostgreSQL`_ ≥ 9.6

.. _`Git`: https://git-scm.com/
.. _`Python`: https://www.python.org/
.. _`Node.js`: https://nodejs.org
.. _`Yarn`: https://yarnpkg.com/
.. _`PostgreSQL`: https://www.postgresql.org/

HAWC developer environment setup
--------------------------------

Instructions below have been written for bash, so should work out of the box for linux/mac. They may need to be adapted slightly for Windows due to the differences in python apps on different operating systems. Clone the repository and install all requirements into a virtual environment:

.. code-block:: bash

    # clone repository; we'll put in ~/dev but you can put anywhere
    mkdir -p ~/dev
    cd ~/dev
    git clone https://github.com/shapiromatron/hawc.git

    # create virtual environment and install requirements
    cd ~/dev/hawc
    python -m venv venv

    # activate the environment
    source ./venv/bin/activate

    # install requirements
    ./venv/bin/pip install -r ./requirements/dev.txt

    # create local settings and modify default settings in this file
    cp ./hawc/main/settings/local.example.py ./hawc/main/settings/local.py

Currently HAWC has two possible application "flavors", where the application is slightly
different depending on which flavor is selected. To change, modify the ``HAWC_FLAVOR``
variable ``hawc/main/settings/local.py``. Possible values include:

- PRIME (default application; as hosted at https://hawcproject.org)
- EPA (EPA application; as hosted at EPA)

Loading a database dump:

.. code-block:: bash

    # add hawc superuser
    createuser hawc --superuser --no-password

    # create new database owned by a hawc user
    createdb -O hawc hawc

    # load gzipped database
    gunzip -c "db_dump.sql.gz" | psql -U hawc -d hawc

For reference, here's how to create a database dump:

.. code-block:: bash

    # anonymize data
    manage.py scrub_db

    # dump in gzipped format
    pg_dump -U hawc hawc | gzip > db_dump.sql.gz

Running the application
~~~~~~~~~~~~~~~~~~~~~~~

You'll need to run both the python webserver and the node webserver to develop
HAWC; here are instructions how how to do both.

In one terminal, start the the python webserver:

.. code-block:: bash

    # create a PostgreSQL database
    createdb -E UTF-8 hawc

    # active python virtual environment
    cd ~/dev/hawc
    source ./venv/bin/activate

    # sync db state with application state
    manage.py migrate

    # run development webserver
    manage.py runserver

In a new terminal, run the node development webserver for javascript:

.. code-block:: bash

    # navigate to frontend folder
    cd ~/dev/hawc/frontend

    # install javascript dependencies
    yarn install

    # start node hot-reloading server
    npm start

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/


Useful utilities
~~~~~~~~~~~~~~~~

There are a number of helpful utility commands in the ``Makefile``. View the makefile to
see how to run manually.  Note that code-formatting and linting is now required; there are checks
set-up in continuous integration that enforce these rules:

.. code-block:: bash

    # run unit tests
    make test

    # format and lint python code
    make format-py

    # format and lint javascript code
    make format-js

    # use the bundled dev `tmux` dev environment
    make dev

If you don't have ``Make`` in your developer environment, you can just call the commands as they're written in the Makefile.

FAQ
~~~

- If tests aren't working after the database has changed (ie., migrated); try dropping the test-database. You can use the command `dropdb test_hawc-fixture-test`, assuming your user has admin rights to delete databases.

Building a test database
~~~~~~~~~~~~~~~~~~~~~~~~

A test database is loaded to run unit tests. The database may need to be periodically updated as new feature are added. To load, make edits, and export the test database:

.. code-block:: bash

    # specify that we're using the unit-test settings
    export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"

    # load existing test
    createdb hawc-fixture-test
    manage.py load_test_db

    # now make edits to the database using the GUI or via command line

    # export database
    manage.py dump_test_db

Visual Studio Code settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example folder-level configuration setting for `Visual Studio Code`_ (recommended HAWC editor):

.. _`Visual Studio Code`: https://code.visualstudio.com/

.. code-block:: json

    {
        "restructuredtext.linter.disabled": true,
        "[html]": {
            "editor.formatOnSave": false
        },
        "[python]": {
            "editor.formatOnSave": true
        },
        "[javascript]": {
            "editor.formatOnSave": false,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": true
            }
        },
        "editor.formatOnSave": true,
        "python.pythonPath": "./venv/bin/python",
        "python.linting.flake8Args": [
            "--config=.flake8"
        ],
        "eslint.workingDirectories": [
            "./frontend"
        ]
    }


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

