# Development

Below you will find basic setup and deployment instructions for the Health
Assessment Workspace Collaborative project.  To begin you should have the
following applications installed on your local development system:

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/)
- [Node.js](https://nodejs.org) LTS v22
- [Yarn](https://yarnpkg.com/) < 2
- [PostgreSQL](https://www.postgresql.org/) >= 16

When writing code for HAWC, there are a few requirements for code acceptance. We have built-in CI using github actions for enforcement:

- Python code must comply with code formatters and linters: ruff
- Javascript code must comply with eslint formatters
- All unit-test must pass; please write test when contributing new code

See below for more details on how to automatically lint/format your code.

## Environment setup

HAWC can be developed on Windows, Linux, or Mac. Development on Mac/Linux is preferred as it is more similar to deployment.

Install [uv](https://docs.astral.sh/uv/); either via pip install or following the installation guide on the website.  Using `uv` is not required; you can build using standard Python + pip or Conda, depending on your personal preference.

```bash title="Mac/Linux"
# clone repository; we'll put in ~/dev but you can put anywhere
mkdir -p ~/dev
cd ~/dev
git clone https://github.com/shapiromatron/hawc.git

# create virtual environment
cd ~/dev/hawc
uv venv --python=3.13

# activate the environment
source ./.venv/bin/activate

# install requirements
uv pip install -e ".[dev,docs]"
uv pip install -e client

# create a PostgreSQL database and superuser
createuser --superuser --no-password hawc
createdb -E UTF-8 -U hawc hawc
```

For Windows, using Anaconda or Miniconda is preferred for additional dependencies:

```batch title="Windows"
:: create a conda environment with our hard to get dependencies
conda create --name hawc
conda activate hawc
conda install python=3.13 postgresql
conda install -c conda-forge nodejs
conda install -c conda-forge yarn=1.22.19

:: clone repository; we'll put in dev but you can put anywhere
mkdir %HOMEPATH%\dev
cd %HOMEPATH%\dev
git clone https://github.com/shapiromatron/hawc.git

:: (optional) if uv is not already installed
python -m pip install -U uv

:: install python requirements
cd %HOMEPATH%\dev\hawc
uv pip install -e ".[dev,docs]"
uv pip install -e client

:: setup and start PostgreSQL; in this example we'll put it in dev
cd %HOMEPATH%\dev
mkdir pgdata
pg_ctl -D pgdata initdb
mkdir pgdata\logs
pg_ctl -D pgdata -l pgdata\logs\logfile start

:: create our superuser and main/test databases
createuser --superuser --no-password hawc
createdb -T template0 -E UTF8 hawc
createdb -T template0 -E UTF8 hawc-test
```

## Running the application

After installing hawc above, you can access the hawc application management commands using the `manage` command in your terminal. You can also use `manage.py` on mac or linux; this was done to mirror the django [manage.py](https://docs.djangoproject.com/en/4.1/ref/django-admin/) convention.

### Linux/Mac

In the first terminal, let's create our database and then run the python webserver:

```bash title="Terminal #1"
# active python virtual environment
cd ~/dev/hawc
source ./.venv/bin/activate

# update python/js packages; sync app state with database
poe sync-dev

# run development webserver  (use one of these commands)
uv run poe run-py
```

In a second terminal, run the node development webserver for javascript:

```bash title="Terminal #2"
# navigate to frontend folder
cd ~/dev/hawc/frontend

# install javascript dependencies
yarn install

# start node hot-reloading server
uv run poe run-py
```

If you navigate to [localhost](http://127.0.0.1:8000/) and see a website, you're ready to begin coding!

### Windows

In the first terminal, let's create our database and then run the python webserver:

```batch title="Terminal #1"
:: activate our environment
conda activate hawc

:: start the postgres database (if not already started)
pg_ctl -D %HOMEPATH%\dev\pgdata -l %HOMEPATH%\dev\pgdata\logs\logfile start

:: update python/js packages; sync app state with database
poe sync-dev

:: run development webserver  (use one of these commands)
poe run-py
```

In a second terminal, run the node development webserver for javascript:

```batch title="Terminal #2"
:: activate our environment
conda activate hawc

:: navigate to frontend folder
cd %HOMEPATH%\dev\hawc\frontend

:: install javascript dependencies
yarn install

:: start node hot-reloading server
poe run-js
```

If you navigate to [localhost](http://127.0.0.1:8000/) and see a website, you're ready to begin coding!

### Useful utilities

There are a number of helpful utility commands available from the command line.

```bash
# show all available commands
poe

# run unit tests
poe test
poe test-js

# run integration tests
poe test-integration

# run integration tests with a visible chrome window and debugger
poe test-integration-debug

# lint code (show changes required) - all, javascript-only, or python-only
poe lint
poe lint-js
poe lint-py

# format code (try to make changes) - all,  javascript-only, or python-only
poe format
poe format-js
poe format-py
```

On Windows; if you created the pgdata folder in %HOMEPATH%\dev, there's a short command to start the database

```bash
# start postgres db (if pgdata folder is located in %HOMEPATH%\dev)
poe startdb
```

### Pre commit hooks

There are number of code quality checks that standardize and format code to make sure that our source code is consistent regardless of the developer. These checks are automatically run when the code is submitted for review, and the linting checks must pass to have a valid review. However, this can be a surprise if you don't run the linters prior to pushning a commit.

The development environment includes [pre-commit](https://pre-commit.com/) to automatically check linters and formatters prior to committing changes.  This would prevent you from pushing code that hadn't been run through the linters. To set up pre-commit, run the following command:

```bash
pre-commit install

# run on all files to make sure it is installed correctly
pre-commit run --all-files
```

!!! note

    This is completely optional; you can use if you wish but it's not required.

## Local Settings

### Django settings inheritance

HAWC settings are structured according to the django settings framework. Within ``hawc/main/settings``, there are a number of settings files that inherit using the following pattern:

```text
            -------------------
            |  HAWC SETTINGS  |
            -------------------
                    |
                    |
                -----------
                | base.py |
                -----------
                /        \
                /          \
    --------------       ----------        ------------
    | staging.py |       | dev.py |  <---  | local.py |
    --------------       ----------        ------------
            |                  |             (applied to dev.py,
            |                  |                 if file exists)
    -----------------    ---------------
    | production.py |    | unittest.py |
    -----------------    ---------------
```

To make changes to your local environment, create (and then modify) ``hawc/main/settings/local.py``. This file is not created by default (and is not tracked in git), but a template can be copied and renamed from ``hawc/main/settings/local.example.py`` as a starting point. You can make changes to this file to configure your local environment, such as which database is used or the "flavor" of HAWC (see "More Settings").

## Testing HAWC

### The test database

A test database is automatically loaded each time you run the unit tests; it contains simplistic data for every model in HAWC.

This makes the test database useful when writing new features. There are multiple users you can use, each with their own global and assessment-level permissions. If you have the test database loaded in, you can log in using the credentials below:

 Role                | Email                    | Password
---------------------|--------------------------|----------
 **Administrator**   | admin@hawcproject.org    | pw
 **Project manager** | pm@hawcproject.org       | pw
 **Team member**     | team@hawcproject.org     | pw
 **Reviewer**        | reviewer@hawcproject.org | pw


There are currently four assessments in the database:

ID | Name | Editable | Public
---|---|---|---
1 | Chemical Z | Yes | No
2 | Chemical X | No | Yes
3 | Chemical Y | Yes | Yes
4 | Chemical A | Yes | No

As new features are added, adding and changing content in the test database will be required to test these features. Instructions for loading and dumping are described below.

#### Generating the test database

Follow the instructions below to generate a test database.

```bash title="Mac/Linux"
# specify that we're using the unit-test settings
export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"

# load existing test
createdb hawc-fixture
manage load_test_db

# now make edits to the database using the GUI or via command line

# export database
manage dump_test_db
```

```batch title="Windows"
:: specify that we're using the unit-test settings
set DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest

:: load existing test
createdb -T template0 -E UTF8 hawc-fixture
manage load_test_db

:: now make edits to the database using the GUI or via command line

:: export database
manage dump_test_db
```

If tests aren't working after the database has changed (ie., migrated); try dropping the test-database with the command ``dropdb hawc-test``.

Some tests compare large exports on disk to ensure the generated output is the same as expected. In some cases, these export files should changes. Therefore, you can set a flag in the `tests/conftest.py` to set `rewrite_data_files` to True. This will rewrite all saved files, so please review the changes to ensure they're expected. A test is in CI to ensure that `rewrite_data_files` is False.

### Loading a database dump

If you have a database dump saved locally, you can load that in instead. If you have multiple databases, you can switch them on the fly in your local.py settings (see Django Settings Inheritance above).

```bash

# add hawc superuser
createuser hawc --superuser --no-password

# create new database owned by a hawc user
createdb -O hawc hawc

# load gzipped database
gunzip -c "db_dump.sql.gz" | psql -U hawc -d hawc
```

### Creating a database dump

Here's how to create a database dump:

```bash
# anonymize data
manage scrub_db

# dump in gzipped format
pg_dump -U hawc hawc | gzip > db_dump.sql.gz
```

### Mocking external resources in tests

When writing tests for code that accesses external resources (e.g., data from PubMed API endpoints), the ``vcr`` python package is used to save "cassettes" of expected responses for faster tests and stability in case external resources are intermittently offline. Periodically we may need to  delete the ``cassettes`` directory and run the python test suite, which will recreate the cassettes based on actual responses.

If a test uses an external resource, ensure that it is decorated with ``@pytest.mark.vcr`` to generate a cassette; see our current tests suite for examples.

To run tests without using the cassettes and making the network requests, use:

```bash
py.test --disable-vcr
```

### Testing celery application

The following requires ``redis-cli`` and ``docker-compose``.

To test asynchronous functionality in development, modify your ``hawc/main/settings/local.py``:

```python
CELERY_BROKER_URL = "redis://:default-password@localhost:6379/1"
CELERY_RESULT_BACKEND = "redis://:default-password@localhost:6379/2"
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
```

Then, create the example docker container and start a celery worker instance:

```bash
# build container
docker-compose -f compose/dc-build.yml --project-directory . build redis
docker-compose -f compose/dc-build.yml --project-directory . up -d redis

# check redis is up and can be pinged successfully
redis-cli -h localhost -a default-password ping

# start workers
celery --app=hawc.main.celery worker --loglevel=INFO
celery --app=hawc.main.celery beat --loglevel=INFO

# stop redis when you're done
docker-compose -f compose/dc-build.yml --project-directory . down
```

Asynchronous tasks will not be executed by celery workers instead of the main thread.

### Integration tests

While the standard tests check that the backend views and models interact as designed, integration testing checks whether the frontend of HAWC functions in a browser as intended. These tests use [playwright](https://playwright.dev/python/). By default, integration tests are skipped when running pytest locally by default, but are always executed in github actions. To run:

```bash title="Mac/Linux"
# to run all
poe test-integration-debug

# or a custom method to run a single test
export INTEGRATION_TESTS=1
py.test -sv tests/integration/test_login.py --pdb
```

```batch title="Windows"
:: to run all
poe test-integration-debug

:: or a custom method to run a single test
set INTEGRATION_TESTS=1
py.test -sv tests/integration/ --pdb
```

It can be helpful to record interactions initially when writing an integration test. This can be done using this command:

```bash
playwright codegen 127.0.0.1:8000
```

By default, the integration tests run in "headless" mode, or without a browser being shown. When editing integration tests, use the interactive mode to capture user operations:

```bash
poe test-integration-debug

# use set instead of export on windows
export INTEGRATION_TESTS=1
export PWDEBUG=1
py.test -sv tests/integration/test_myuser.py --pdb
```

Sometimes you may want to run a test multiple times to check for flakiness:

```bash
for i in {1..10}; do
INTEGRATION_TESTS=1 py.test -sv tests/integration/ -k test_example
done
```

## More settings

### Visual Studio Code

[Visual Studio Code]( https://code.visualstudio.com/) is the recommended editor for this project. Recommended extensions include:

- [Python for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Eslint for VS Code](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)

When using the recommended settings below, your python and javascript code should automatically format whenever you save to fix most, but not all requirements. In addition, you should have pretty good autocompletion. Python type annotations are enabled with warnings, but not enforced; this may change as we continue to annotate the existing codebase. You can add these settings to your overall VSCode settings.json file, or create a [workspace](https://code.visualstudio.com/docs/editor/workspaces) for HAWC and add it to the workspace settings.json file.

```json
{
    "[dockerfile]": {
        "editor.formatOnSave": false
    },
    "[css]": {
        "editor.formatOnSave": false,
    },
    "[javascript]": {
        "editor.formatOnSave": false,
    },
    "[markdown]": {
        "editor.wordWrap": "bounded",
        "editor.quickSuggestions": false
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true
        },
    },
    "editor.codeActionsOnSave": {
        "source.fixAll": false,
        "source.fixAll.eslint": true
    },
    "editor.formatOnPaste": false,
    "editor.formatOnSave": false,
    "editor.rulers": [100, 120],
    "editor.tabSize": 4,
    "eslint.format.enable": true,
    "files.eol": "\n",
    "files.exclude": {
        "**/*.pytest_cache": true,
        "**/__pycache__": true
    },
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true,
    "python.analysis.diagnosticSeverityOverrides": {
        "reportUnknownMemberType": "information",
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.languageServer": "Pylance",
    "python.linting.flake8Enabled": false,
    "search.exclude": {
        "**/node_modules": true,
        "**/.git": true,
    },
}
```

### HAWC flavors

Currently HAWC has two possible application "flavors", where the application is slightly different depending on which flavor is selected. To change, modify the ``HAWC_FLAVOR`` variable at ``hawc/main/settings/local.py``.

Possible values include:

- PRIME (default application; as hosted at <https://hawcproject.org>)
- EPA (EPA application; as hosted at EPA)

### Updating EPA.gov style

There are multiple styles available when using HAWC; and the EPA style has to be updated periodically for the same look at feel as the EPA website. The following steps describe how to update HAWC styling with the EPA theme:

1.  In your browser, go to the [EPA Template](https://www.epa.gov/themes/epa_theme/pattern-lab/patterns/pages-standalone-template/pages-standalone-template.rendered.html) site. We recommend Firefox or Internet Explorer.
2.  Right click the page and select "Save As" to download the page as an .html file.
3. Open the downloaded `EPA Template_US EPA_files` folder.
4. Open `styles.css` in VS Code.
5. Replace the contents of `hawc/static/css/epa/core/style.css` with the updated `styles.css`.
    *  Edit font locations in style sheet to point to `//www.epa.gov/themes/epa_theme/` instead of relative paths
6. Overwrite any necessary changes in `hawc/static/css/epa-hawc.css` to maintain HAWC styling.
7. Test changes locally to ensure HAWC matches EPA.gov styling.  On the base.html, you may want to disable caching for the header and footer components (or cache for 1 second) so it makes it easier to see the changes.

A few revisions were made to USWDS assets:

* Update the fonts path location to pull from an external delivery network instead of the `../fonts` location in the styles.css file. This was done using a search/replace on that file.

### Materialized views

HAWC is in essence two different systems with very different data requirements:

1. It is a content-management capture system for data used in systematic reviews
2. It is a data visualization and summarization system of these data

To facilitate #2, materialized views have been added and other caching systems to precompute views
of the data frequently used for generate data visuals and other insights. In production, materialized
views are refreshed daily via a persistent celery task, as well as up to every five minutes if a
flag for updating the data is set.

In development however, we generally do not run the celery task service in the backend. Thus, to
trigger a materialized view rest, you can use a `manage` command:

```bash
manage refresh_views
```

You may need to do this periodically if your data is stale.

### Lines of code

To generate a report on the lines of code, install [cloc](https://github.com/AlDanial/cloc) and then run the make command:

```bash
poe loc
```

### Testing the client

Most tests for the `hawc-client` package are integrated into our standard test suite using pytest. However, the interactive tests which require interacting with the HTML DOM to download figures and images couldn't be integrated into the standard test suite without significant effort. Therefore, it requires manually running a test using our test fixture.

To run this script, start the django webserver using the hawc-fixture database. It must be running on port 8000, and the django webserver as well as the node javascript server. Make sure that the django debug toolbar is not enabled:

```bash
export "DJANGO_SETTINGS_MODULE=hawc.main.settings.unittest"
createdb -U hawc-fixture
python manage.py load_test_db
python scripts/test_iclient.py
```

Make sure the standard unit tests pass as well as the addition `test_iclient.py` tests before distributing a new version of the `hawc-client` package.

### Testing with Turnstile

Turnstile can be enabled for human verification on select views in HAWC, generally related to authentication requests. For testing (in development mode), use the following keys keys in django settings:

```py
TURNSTILE_SITE = "1x00000000000000000000AA"  # always passes, or
TURNSTILE_SITE = "2x00000000000000000000AB"  # always blocks
TURNSTILE_KEY = "1x0000000000000000000000000000000AA"  # valid key
```

These options are described in detail in the turnstile testing [documentation](https://developers.cloudflare.com/turnstile/reference/testing/).
