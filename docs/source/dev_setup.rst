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

While development has previously been setup using the Windows operating
environment, it is recommended to use a Mac/Linux environment for development,
as it better reflects the server-environment and is generally much easier
to develop Python applications with a system can can compile C code natively.


Getting Started
---------------

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv hawc
    $VIRTUAL_ENV/bin/pip install -r $PWD/requirements/dev.txt

Then create a local settings file and set your ``DJANGO_SETTINGS_MODULE`` to
use it::

    cp project/hawc/settings_local.example.py project/hawc/settings_local.py
    echo "export DJANGO_SETTINGS_MODULE=hawc.settings" >> $VIRTUAL_ENV/bin/postactivate
    echo "unset DJANGO_SETTINGS_MODULE" >> $VIRTUAL_ENV/bin/postdeactivate

Exit the virtualenv and reactivate it to activate the settings just changed::

    deactivate
    workon hawc

Create the Postgres database and run the initial syncdb/migrate::

    createdb -E UTF-8 hawc
    python manage.py syncdb

Note that django-reversion needs to have two additional migrations to use the custom HAWC user-model. To apply this migration, copy the migrations in `hawc/utils/reversion` to the correct location where reversion is installed on your computer, and then apply migrations::

    python manage.py migrate

You should now be able to run the development server::

    python manage.py runserver

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/
