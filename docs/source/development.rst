Development
===========

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- `Git`_
- `Python`_ == 3.9
- `Node.js`_
- `Yarn`_
- `PostgreSQL`_ ≥ 9.6

.. _`Git`: https://git-scm.com/
.. _`Python`: https://www.python.org/
.. _`Node.js`: https://nodejs.org
.. _`Yarn`: https://yarnpkg.com/
.. _`PostgreSQL`: https://www.postgresql.org/

When writing code for HAWC, there are a few requirements for code acceptance. We have built-in CI using github actions for enforcement:

- Python code must comply with code formatters and linters: black, flake8, and isort
- Javascript code must comply with eslint formatters
- All unit-test (currently in python-only) must pass; please write test when contributing new code

See the `Useful utilities`_ below for more details on how to automatically lint/format your code.

Environment setup
-----------------

HAWC can be developed both on Windows and and Linux/Mac. Development on Mac/Linux is preferred as it is more similar to the deployment environments, and things are a little more out of the box. However, instructions are provided below for both environments.

Linux/Mac
~~~~~~~~~

Instructions below have been written for bash, so should work out of the box for Linux/Mac. Clone the repository and install all requirements into a virtual environment:

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

    # create a PostgreSQL database and superuser
    createuser --superuser --no-password hawc
    createdb -E UTF-8 -U hawc hawc



Windows
~~~~~~~

Windows requires using anaconda, or miniconda to get requirements.

.. code-block:: bat

    :: create a conda environment with our hard to get dependencies
    conda create --name hawc
    conda activate hawc
    conda install python=3.9 postgresql=9.6
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

Running the application
-----------------------

After initial setup, here are the steps needed to run the application in development.

Linux/Mac
~~~~~~~~~

In the first terminal, let's create our database and then run the python webserver:

.. code-block:: bash

    # active python virtual environment
    cd ~/dev/hawc
    source ./venv/bin/activate

    # sync db state with application state
    manage.py migrate

    # run development webserver
    manage.py runserver

In a second terminal, run the node development webserver for javascript:

.. code-block:: bash

    # navigate to frontend folder
    cd ~/dev/hawc/frontend

    # install javascript dependencies
    yarn install

    # start node hot-reloading server
    npm start

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/

Windows
~~~~~~~

In the first terminal, let's create our database and then run the python webserver:

.. code-block:: bat

    :: activate our environment
    cd %HOMEPATH%\dev\hawc
    conda activate hawc
    venv\Scripts\activate

    :: start the postgres database (if not already started)
    pg_ctl -D %HOMEPATH%\dev\pgdata -l %HOMEPATH%\dev\pgdata\logs\logfile start

    :: run the python webserver
    manage.py runserver

In a second terminal, run the node development webserver for javascript:

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

There are a number of helpful utility commands available from the command line. Depending on the
OS, they're either available in the ``Makefile`` or ``make.bat``, but they can be called using
the same commands.

.. code-block:: bash

    # run unit tests
    make test

    # lint code (show changes required) - all, javascript-only, or python-only
    make lint
    make lint-js
    make lint-py

    # format code (try to make changes) - all,  javascript-only, or python-only
    make format
    make format-js
    make format-py

On Mac/Linux; if you have tmux installed, there's a one-line command to start the environment

.. code-block:: bash

    # use the bundled dev `tmux` dev environment
    make dev

Visual Studio Code
------------------

`Visual Studio Code`_ is the recommended editor for this project.

.. _`Visual Studio Code`: https://code.visualstudio.com/

Recommended extensions:

- `Python for vscode`_
- `Eslint for vscode`_
- `Code Spell Checker`_

.. _`Python for vscode`: https://marketplace.visualstudio.com/items?itemName=ms-python.python
.. _`Eslint for vscode`: https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint
.. _`Code Spell Checker`: https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker

When using the recommended settings below, your python and javascript code should automatically format whenever you save to fix most, but not all requirements. In addition, you should have pretty good autocompletion. Python type annotations are enabled with warnings, but not enforced; this may change as we continue to annotate the existing codebase.

.. code-block:: json

    {
        "restructuredtext.linter.disabled": true,
        "[html]": {
            "editor.formatOnSave": false
        },
        "[python]": {
            "editor.formatOnPaste": false,
            "editor.formatOnSave": true
        },
        "[javascript]": {
            "editor.formatOnSave": false,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": true
            }
        },
        "editor.formatOnSave": true,
        "eslint.workingDirectories": [
            "./frontend"
        ],
        "python.formatting.provider": "black",
        "python.jediEnabled": false,
        "python.languageServer": "Microsoft",
        "python.linting.flake8Args": [
            "--config=.flake8"
        ],
        "python.linting.flake8Enabled": true,
        "python.linting.mypyCategorySeverity.error": "Warning",
        "python.linting.mypyEnabled": true,
        "python.pythonPath": "./venv/bin/python",
        "cSpell.words": [
            "chemspider",
            "epimeta",
            "invitro",
            "lel",
            "loael",
            "loel",
            "mgmt",
            "nel",
            "noael",
            "noel",
            "noel",
            "pmid",
            "pmids",
            "transfection",
        ]
    }

More settings
-------------

HAWC flavors
~~~~~~~~~~~~

Currently HAWC has two possible application "flavors", where the application is slightly
different depending on which flavor is selected. To change, modify the ``HAWC_FLAVOR``
variable ``hawc/main/settings/local.py``. Possible values include:

- PRIME (default application; as hosted at https://hawcproject.org)
- EPA (EPA application; as hosted at EPA)

The test database
~~~~~~~~~~~~~~~~~

Loading a database dump:

.. code-block:: bash

    # add hawc superuser
    createuser hawc --superuser --no-password

    # create new database owned by a hawc user
    createdb -O hawc hawc

    # load gzipped database
    gunzip -c "db_dump.sql.gz" | psql -U hawc -d hawc

Creating a database dump
~~~~~~~~~~~~~~~~~~~~~~~~

Here's how to create a database dump:

.. code-block:: bash

    # anonymize data
    manage.py scrub_db

    # dump in gzipped format
    pg_dump -U hawc hawc | gzip > db_dump.sql.gz

The test database
~~~~~~~~~~~~~~~~~

A test database is loaded to run unit tests.

The test database can be useful when writing new feature as well. If you use the database for feature development, there are multiple users you can use, with their global and assessment-level permissions, emails, and passwords below:

+---------------------+--------------------------+----------+
| Role                | Email                    | Password |
+=====================+==========================+==========+
| **Administrator**   | admin@hawcproject.org    | pw       |
+---------------------+--------------------------+----------+
| **Project manager** | pm@hawcproject.org       | pw       |
+---------------------+--------------------------+----------+
| **Team member**     | team@hawcproject.org     | pw       |
+---------------------+--------------------------+----------+
| **Reviewer**        | reviewer@hawcproject.org | pw       |
+---------------------+--------------------------+----------+

As new features are added, adding and changing content in the test-database will be required to test these features. Instructions for loading and dumping are described below.

Linux/Mac
~~~~~~~~~
.. code-block:: bash

    # specify that we're using the unit-test settings
    export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"

    # load existing test
    createdb hawc-fixture-test
    manage.py load_test_db

    # now make edits to the database using the GUI or via command line

    # export database
    manage.py dump_test_db

Windows
~~~~~~~~~
.. code-block:: bat

    :: specify that we're using the unit-test settings
    set DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest

    :: load existing test
    createdb -T template0 -E UTF8 hawc-fixture-test
    manage.py load_test_db

    :: now make edits to the database using the GUI or via command line

    :: export database
    manage.py dump_test_db

If tests aren't working after the database has changed (ie., migrated); try dropping the test-database. Try the command ``dropdb test_hawc-fixture-test``.

Some tests compare large exports on disk to ensure the generated output is the same as expected. In some cases, these export files should changes. Therefore, you can set a flag in the `tests/conftest.py` to set `rewrite_data_files` to True. This will rewrite all saved files, so please review the changes to ensure they're expected. A test is in CI to ensure that `rewrite_data_files` is False.

Mocking external resources in tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When writing tests that require accessing external resources, the ``vcr`` python package is used to save "cassettes" of expected responses to allow faster tests and stability in case external resources are intermittently offline. These cassettes can be rebuilt by running ``make test-refresh``, which will delete the ``cassettes`` directory and run the python test suite, which in turn recreates the cassettes based on actual responses.

If a test uses an external resource, ensure that it is decorated with ``@pytest.mark.vcr`` to generate a cassette; see our current tests suite for examples.

To run tests without using the cassettes and making the network requests, use:

.. code-block:: bash

    py.test --disable-vcr


Testing celery application
~~~~~~~~~~~~~~~~~~~~~~~~~~

To test asynchronous functionality in development, modify your ``hawc/main/settings/local.py``:

.. code-block:: python

    CELERY_BROKER_URL = "redis://:default-password@localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://:default-password@localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER = False
    CELERY_TASK_EAGER_PROPAGATES = False

Then, create the example docker container and start a celery worker instance:

.. code-block:: bash

    # build container
    docker-compose -f compose/dc-build.yml --project-directory . build redis
    docker-compose -f compose/dc-build.yml --project-directory . up -d redis

    # check redis is up and can be pinged successfully
    redis-cli -h localhost -a default-password ping

    # start workers
    celery worker --app=hawc.main.celery --loglevel=INFO
    celery beat --app=hawc.main.celery --loglevel=INFO

    # stop redis when you're done
    docker-compose -f compose/dc-build.yml --project-directory . down

Asynchronous tasks will no be executed by celery workers instead of the main thread.

Integration tests
~~~~~~~~~~~~~~~~~

Integration tests use selenium and Firefox or Chrome for for testing. By default, integration tests are skipped. Firefox appears to be more stable based on initial investigation for these tests To run, you'll need to set a few environment variables.

.. code-block:: bash

    export HAWC_INTEGRATION_TESTS=1
    export SHOW_BROWSER=1            # or 0 for headless
    export BROWSER="firefox"         # or "chrome"
    py.test -sv tests/frontend/integration/ --pdb

When writing these tests, it's often easiest to write the tests in an interactive scripting environment like ipython or jupyter. This allows you to interact with the DOM and the requests much easier than manually re-running tests as they're written. An example session:

.. code-block:: python

    import helium as h
    from selenium.webdriver import FirefoxOptions

    driver = h.start_firefox(headless=False)
    driver.set_window_size(1920, 1080)

    h.go_to("https://hawcproject.org")
    h.click("Login")
    assert "/user/login/" in driver.current_url

    # ... keep coding here, use introspection in python as well as debugger tools for testing...

    # cleanup
    driver.close()

Then, transfer the interactive potions into unit-tests...

Materialized views and reporting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HAWC is in essence two different systems with very different data requirements:

1. It is a content-management capture system for data used in systematic reviews
2. It is a data visualization and summarization system of these data

To facilitate #2, materialized views have been added and other caching systems to precompute views
of the data frequently used for generate data visuals and other insights. In production, materialized
views are refreshed daily via a persistent celery task, as well as up to every five minutes if a
flag for updating the data is set.

In development however, we generally do not run the celery task service in the backend. Thus, to
trigger a materialized view rest, you can use a manage.py command:

.. code-block:: bash

    manage.py refresh_views

You may need to do this periodically if your data is stale.

Distributing HAWC clients
~~~~~~~~~~~~~~~~~~~~~~~~~

The Python HAWC client can be packaged for easy distribution.

.. code-block:: bash

    # install dependencies
    pip install twine wheel

    # change to client path
    cd client

    # build packages; these can be distributed directly
    make build

    # or can be uploaded to pypi
    make upload-testpypi
    make upload-pypi

Lines of code
~~~~~~~~~~~~~

To generate a report on the lines of code, install cloc_ and then run the make command:

.. code-block:: bash

    make loc

.. _cloc: https://github.com/AlDanial/cloc

