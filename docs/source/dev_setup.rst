Development Setup
=================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- Python 2.7
- `Node.js >= 4.0 <https://nodejs.org/>`_
- `Npm.js >= 3.0 <https://npmjs.org/>`_
- `pip >= 8.1 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.9 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.5 <http://pypi.python.org/pypi/virtualenvwrapper>`_ (mac/linux)
- `virtualenvwrapper-win >= 1.2.1 <https://pypi.python.org/pypi/virtualenvwrapper-win>`_. (windows)
- Postgres >= 9.3
- git >= 1.7


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

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv hawc
    git clone https://github.com/shapiromatron/hawc.git
    cd hawc
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

Create a local settings file and update the necessary fields within the settings::

    cp hawc/settings/local.example.py hawc/settings/local.py

Next, update your virtual-environment settings in ``$VIRTUAL_ENV/bin/postactivate``::

    #!/bin/sh
    # This hook is sourced after this virtualenv is activated.

    # required to install psycopg2 on Mac
    export "PATH=/Library/PostgreSQL/9.4/bin:${PATH}"

    # django environment-variable settings
    export "DJANGO_SETTINGS_MODULE=hawc.settings.local"
    export "DJANGO_STATIC_ROOT=$HOME/dev/temp/hawc/static"
    export "DJANGO_MEDIA_ROOT=$HOME/dev/temp/hawc/media"

    # move to project path
    cd $HOME/dev/hawc/project

Windows
~~~~~~~~~

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv hawc
    git clone https://github.com/shapiromatron/hawc.git

To install python packages, ensure you have the Python C++ compiler, available
from `Microsoft <https://www.microsoft.com/en-us/download/details.aspx?id=44266>`_. Also
ensure that your version of pip allows for installation of wheels (v8 or higher).
Install numpy and scipy using precompiled binaries, available for download from
`Christoph Gohlke <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_ (they're difficult to build on Windows),
by using these commands (adapted to the filename/location on your computer)::

    pip install "C:\Users\username\Desktop\numpy-version.whl"
    pip install "C:\Users\username\Desktop\scipy-version.whl"

Then, you should be able to install remaining packages via pip::

    cd hawc
    pip install -r requirements/windows/dev.txt

Create a local settings file and update the necessary fields within the settings::

    copy project\hawc\settings\local.example.py project\hawc\settings\local.py

Next, add these values to the bottom of the ``activate.bat`` file, which should be
located in ``%VIRTUAL_ENV%\Scripts\activate.bat``::

    :: django environment-variable settings
    set "DJANGO_SETTINGS_MODULE=hawc.settings.local"
    set "DJANGO_STATIC_ROOT=%USERPROFILE%\dev\temp\hawc\static"
    set "DJANGO_MEDIA_ROOT=$HOME\dev\temp\hawc\media"

    :: move to project path (change to correct path)
    cd %USERPROFILE%\dev\hawc\project"

HAWC setup: Part II
-------------------

start the virtual environment::

    deactivate
    workon hawc

Create a PostgreSQL database and run the initial syncdb/migrate::

    createdb -E UTF-8 hawc

Next, we'll run a few management command and apply migrations::

    python manage.py build_d3_styles
    python manage.py migrate
    python manage.py createcachetable

You should now be able to run the python backend development server::

    python manage.py runserver

Next, you'll need to setup the front-end web bundler. Make sure the ``npm``
command is accessible from your virtual environment. In the ``/project`` path,
run the following command, which will install all javascript packages for our
development environment::

    npm install --save-dev

After installing dependencies, run the javascript bundler in a second terminal::

    npm start

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/


Loading a database export:
~~~~~~~~~~~~~~~~~~~~~~~~~~

To load a database export from the `assessment_db_dump` management command,
use the following arguments, if Postgres is available from the command-line::

    dropdb hawc         # if database already exists
    createdb hawc       # create new database
    psql –d hawc –f /path/to/export.sql

If Postgres tools are not available from the command-line, from a pqsl session::

    DROP DATABASE hawc;     --- drop database if exists
    CREATE DATABASE hawc;   --- create new database
    \c hawc                 --- open database
    \i /path/to/export.sql  --- load data into database


Database ER diagrams
~~~~~~~~~~~~~~~~~~~~

To view the HAWC database schema, make sure the `django_extensions`_ package
is required, as well as `pydot`_ and `graphviz`_. Then, run the following
django management commands::

    # create for all apps
    python manage.py graph_models -a -g --pydot -o hawc.png

    # create ER for single apps
    python manage.py graph_models -g --pydot -o utils.png utils
    python manage.py graph_models -g --pydot -o myuser.png myuser
    python manage.py graph_models -g --pydot -o assessment.png assessment
    python manage.py graph_models -g --pydot -o lit.png lit
    python manage.py graph_models -g --pydot -o study.png study
    python manage.py graph_models -g --pydot -o animal.png animal
    python manage.py graph_models -g --pydot -o epi.png epi
    python manage.py graph_models -g --pydot -o epimeta.png epimeta
    python manage.py graph_models -g --pydot -o invitro.png invitro
    python manage.py graph_models -g --pydot -o bmd.png bmd
    python manage.py graph_models -g --pydot -o summary.png summary
    python manage.py graph_models -g --pydot -o comments.png comments

.. _`django_extensions`: https://github.com/django-extensions/django-extensions
.. _`pydot`: https://github.com/erocarrera/pydot
.. _`graphviz`: http://www.graphviz.org/
