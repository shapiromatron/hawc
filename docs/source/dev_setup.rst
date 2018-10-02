Development Setup
=================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- `Git`_
- `Node.js`_
- `Yarn`_
- `PostgreSQL`_ ≥ 9.4 (uses `JSONB`_)
- `Python`_ 3.6+

.. _`Git`: https://git-scm.com/
.. _`Python`: https://www.python.org/
.. _`Node.js`: https://nodejs.org
.. _`Yarn`: https://yarnpkg.com/
.. _`PostgreSQL`: https://www.postgresql.org/
.. _`JSONB`: https://www.postgresql.org/docs/current/static/datatype-json.html


.. warning::
    HAWC can be developed in Windows, however, in versions older than Windows 10,
    it may not be possible due to file-system restrictions. The maximum
    path length in some Windows environments is 260; the Node.js packaging
    system may often exceed this length, and does in the current HAWC environment.

    There's nothing we can do to fix this that we're aware of.


HAWC setup: Part I (OS-specific)
--------------------------------

The initial HAWC setup is operating-system specific, due to limitations in
the ease of installing scientific python software on Windows. Choose your
own adventure below.

Mac/Linux
~~~~~~~~~

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

    # create a local settings file
    cp ./project/hawc/settings/local.example.py ./project/hawc/settings/local.py

Update the settings file with any changes you'd like to make for your local
development environment.

Current HAWC as two possible application "flavors", where the application is slightly
different depending on which flavor is selected. To change, modify the ``HAWC_FLAVOR``
environment variable in the local settings. Possible values include:

- PRIME (default application)
- EPA (EPA application)

Windows
~~~~~~~

To setup your local environment you should create a virtualenv and install the
necessary requirements:

.. code-block:: batch

    :: clone repository; we'll put in ~/dev but you can put anywhere
    mkdir ~/dev
    cd ~/dev
    git clone https://github.com/shapiromatron/hawc.git

    :: create virtual environment and install requirements
    cd ~/dev/hawc
    python -m venv venv
    call ./venv/bin/activate.bat
    $VIRTUAL_ENV/bin/pip install -r ./requirements/dev.txt

    :: create a local settings file
    copy ./project/hawc/settings/local.example.py ./project/hawc/settings/local.py

The ``pip install`` call may fail with some packages on Windows if you don't have
the `Python Microsoft C++ compiler`_ available. You can use prepackaged
binaries available from `Christoph Gohlke`_ using these commands after
downloading the wheels from the website:

.. _`Python Microsoft C++ compiler`: https://www.microsoft.com/en-us/download/details.aspx?id=44266
.. _`Christoph Gohlke`: http://www.lfd.uci.edu/~gohlke/pythonlibs/

.. code-block:: batch

    pip install "C:\Users\username\Desktop\numpy-version.whl"
    pip install "C:\Users\username\Desktop\scipy-version.whl"

Update the settings file with any changes you'd like to make for your local
development environment.

HAWC setup: Part II
-------------------

You'll need to run both the python webserver and the node webserver to develop
HAWC; here are instructions how how to do both.

To run the python webserver:

.. code-block:: bash

    # create a PostgreSQL database
    createdb -E UTF-8 hawc

    # active python virtual environment and sync database schema with code
    cd ~/dev/hawc/project
    source ../venv/bin/activate
    python manage.py build_d3_styles
    python manage.py migrate
    python manage.py createcachetable

    # run development webserver
    python manage.py runserver

In a new terminal, run the node development webserver for javascript:

.. code-block:: bash

    # navigate to project folder
    cd ~/dev/hawc/project

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
