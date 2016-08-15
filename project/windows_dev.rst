Development Setup for Windows
=============================

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- Python 2.7
- `Node.js >= 4.0 <https://nodejs.org/>`_
- `Npm.js >= 3.0 <https://npmjs.org/>`_
- `pip >= 1.5 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.9 <http://www.virtualenv.org/>`_
- `virtualenvwrapper-win >= 1.2.1 <https://pypi.python.org/pypi/virtualenvwrapper-win>`_
- Postgres >= 9.3
- git >= 1.7

Gettings Started
----------------

To setup your local environment you should create a virtualenv and install the
necessary requirements::

    mkvirtualenv hawc
    pip install -r $PWD/requirements/windows/dev.txt

You'll also need to install compiled Windows binaries for scipy<http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>
Just download the .whl file for your system and run `pip install ${file.whl}`.


Create a local settings file and update the necessary fields within the settings::

    copy hawc/settings/local.example.py hawc/settings/local.py

Next, open %PYTHONHOME%/Scripts/workon.bat and add before :END ::

    set "VIRTUALENVWRAPPER_HOOK_DIR=%VIRTUAL_ENV%\hooks"
    if exist "%VIRTUALENVWRAPPER_HOOK_DIR%\postactivate.bat" (
        call "%VIRTUALENVWRAPPER_HOOK_DIR%\postactivate.bat"
    )

Then update your virtual-environment settings in ``%VIRTUALENVWRAPPER_HOOK_DIR%\postactivate.bat``::

    # django environment-variable settings
    set "DJANGO_SETTINGS_MODULE=hawc.settings.local"
    set "DJANGO_STATIC_ROOT=$HOME/dev/temp/hawc/static"
    set "DJANGO_MEDIA_ROOT=$HOME/dev/temp/hawc/media"

    # move to project path
    cd %USERPROFILE%/dev/hawc/project

Re-activate the virtual environment::

    deactivate
    workon hawc

Create a PostgreSQL database by opening the SQL Shell from Start>Programs>PostgreSQL>Sql Shell(psql)::

    create database hawc;

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

    npm run start

If you navigate to `localhost`_ and see a website, you're ready to begin coding!

.. _`localhost`: http://127.0.0.1:8000/
