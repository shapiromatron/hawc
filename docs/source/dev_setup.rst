Development Setup
=================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- Python 2.7
- `pip >= 1.5.6 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.91 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.5 <http://pypi.python.org/pypi/virtualenvwrapper>`_
- Postgres >= 9.1
- git >= 1.7


Getting Started
---------------

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv hawc
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

Create a local settings file and update the necessary fields within the settings::

    cp hawc/settings/local.example.py hawc/settings/local.py

Next, update your virtual-environment settings in ``$VIRTUAL_ENV/bin/postactivate``::

    #!/bin/sh
    # This hook is sourced after this virtualenv is activated.

    # required to install psycopg2 on Mac
    export "PATH=/Library/PostgreSQL/9.4/bin:${PATH}"

    # django environment-variable settings
    export "DJANGO_SECRET_KEY=dge)%8j^94jtu0sioz2%q1ermqp!9f*eq^b_yorddc7_)&^tuf"
    export "DJANGO_SETTINGS_MODULE=hawc.settings.local"
    export "DJANGO_STATIC_ROOT=$HOME/dev/temp/hawc/static"
    export "DJANGO_MEDIA_ROOT=$HOME/dev/temp/hawc/media"

    # move to project path
    cd $HOME/dev/hawc/project

Re-activate the virtual environment::

    deactivate
    workon hawc

Create a PostgreSQL database and run the initial syncdb/migrate::

    createdb -E UTF-8 hawc

Next, we'll run a few management command and apply migrations::

    python manage.py build_d3_styles
    python manage.py syncdb
    python manage.py migrate
    python manage.py createcachetable dev_cache_table

You should now be able to run the development server::

    python manage.py runserver

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/
