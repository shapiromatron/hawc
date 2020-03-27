Development
===========

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- `Git`_
- `Python`_ == 3.6 (recommended to stay on Python 3.6 for some packages)
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

    # create a new PostgreSQL superuser
    createuser --superuser --no-password hawc

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

Testing celery application
~~~~~~~~~~~~~~~~~~~~~~~~~~

To test asynchronous functionality in development, modify your ``hawc/main/settings/local.py``:

.. code-block:: python

    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER = False
    CELERY_TASK_EAGER_PROPAGATES = False

Then, create the example docker container and start a celery worker instance:

.. code-block:: bash

    docker-compose build redis
    docker up -d redis
    celery worker --app=hawc.main.celery --loglevel=INFO --soft-time-limit=90 --time-limit=120

Asynchronous tasks will no be executed by celery workers instead of the main thread.

Visual Studio Code settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Visual Studio Code`_ is the recommended editor for this project.

.. _`Visual Studio Code`: https://code.visualstudio.com/

Recommended extensions:

- `Python for vscode`_
- `Eslint for vscode`_

.. _`Python for vscode`: https://marketplace.visualstudio.com/items?itemName=ms-python.python
.. _`Eslint for vscode`: https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint

Recommended workspace settings:

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

Windows development instructions
--------------------------------

The following steps are necessary to setup a developer environment in Windows.

.. code-block:: bat

    :: create a conda environment with our hard to get dependencies
    conda create --name hawc
    conda activate hawc
    conda install python=3.6 postgresql=9.6
    conda install -c conda-forge nodejs
    conda install -c conda-forge yarn

    :: now create a virtual python environment for our project
    mkdir %HOMEPATH%\dev
    cd %HOMEPATH%\dev
    git clone https://github.com/shapiromatron/hawc.git
    cd hawc

    :: install the python requirements
    conda activate hawc
    python -m venv venv
    venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements\dev.txt

    :: install the javascript requirements
    cd frontend
    yarn

    :: setup our postgres database
    mkdir %HOMEPATH%\dev\pgdata\
    pg_ctl -D %HOMEPATH%\dev\pgdata initdb
    mkdir %HOMEPATH%\dev\pgdata\logs
    pg_ctl -D %HOMEPATH%\dev\pgdata -l %HOMEPATH%\dev\pgdata\logs\logfile start
    createuser --superuser --no-password hawc

    :: create our main and test databases
    createdb -T template0 -E UTF8 hawc
    createdb -T template0 -E UTF8 test_hawc-fixture-test

    :: sync the hawc code with the database
    manage.py migrate

To run the application, you must run the python webserver in one terminal:

.. code-block:: bat

    :: activate our environment
    cd %HOMEPATH%\dev\hawc
    conda activate hawc
    venv\Scripts\activate

    :: start the postgres database
    pg_ctl -D %HOMEPATH%\dev\pgdata -l %HOMEPATH%\dev\pgdata\logs\logfile start

    :: run the python webserver
    manage.py runserver

and the node webserver in another terminal:

.. code-block:: bat

    :: activate our environment
    cd %HOMEPATH%\dev\hawc
    conda activate hawc
    venv\Scripts\activate

    :: run the frontend build server
    cd %HOMEPATH%\dev\hawc\frontend
    npm start

You can check `localhost`_ to see if everything is hosted correctly.

.. _`localhost`: http://127.0.0.1:8000/

Useful utilities
~~~~~~~~~~~~~~~~

There are two batch scripts named ``make`` available which provide most of the utilities found in the ``Makefile``.

One of these is accessible from the project's top directory:

.. code-block:: bat

    :: run python test suite
    make test

    :: format python code
    make format-py

    :: for more commands...
    make help

And another within the project's ``doc`` folder:

.. code-block:: bat

    :: clean all the built documents
    make clean

    :: build documents as html
    make html

    :: for more commands...
    make help
