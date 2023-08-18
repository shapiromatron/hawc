@ECHO off

if "%~1" == "" goto :help
if /I %1 == help goto :help
if /I %1 == sync-dev goto :sync-dev
if /I %1 == build goto :build
if /I %1 == docs goto :docs
if /I %1 == docs-serve goto :docs-serve
if /I %1 == lint goto :lint
if /I %1 == format goto :format
if /I %1 == lint-py goto :lint-py
if /I %1 == format-py goto :format-py
if /I %1 == lint-js goto :lint-js
if /I %1 == format-js goto :format-js
if /I %1 == test goto :test
if /I %1 == test-integration goto :test-integration
if /I %1 == test-integration-debug goto :test-integration-debug
if /I %1 == test-refresh goto :test-refresh
if /I %1 == test-js goto :test-js
if /I %1 == coverage goto :coverage
if /I %1 == loc goto :loc
if /I %1 == startdb goto :startdb
goto :help

:help
echo.Please use `make ^<target^>` where ^<target^> is one of
echo.  sync-dev          sync dev environment after code checkout
echo.  build             build python wheel
echo.  docs              Build documentation
echo.  docs-serve        Generate documentation
echo.  test              run python tests
echo.  test-integration  run integration tests (requires npm run start)
echo.  test-integration-debug   run integration tests in debug mode (requires npm run start)
echo.  test-refresh      removes mock requests and runs python tests
echo.  test-js           run javascript tests
echo.  coverage          run coverage and create html report
echo.  lint              check formatting issues
echo.  format            fix formatting issues where possible
echo.  lint-py           check python formatting issues
echo.  format-py         fix python formatting issues where possible
echo.  lint-js           check javascript formatting issues
echo.  format-js         fix javascript formatting issues where possible
echo.  loc               generate lines of code report
echo.  startdb           start postgres db (if pgdata folder is located in %HOMEPATH%\dev)
goto :eof

:sync-dev
python -m pip install -U pip
python -m pip install -r requirements/dev.txt
yarn --cwd frontend
python manage.py migrate
python manage.py recreate_views
goto :eof

:build
del /f /q .\build .\dist
call npm --prefix .\frontend run build
python manage.py set_git_commit
flit build
goto :eof

:docs
cd docs
mkdocks build --strict
goto :eof

:docs-serve
cd docs
mkdocs serve -a localhost:8010
goto :eof

:lint
black . --check && ruff .
npm --prefix .\frontend run lint
goto :eof

:format
black . && ruff . --fix --show-fixes
npm --prefix .\frontend run format
goto :eof

:lint-py
black . --check && ruff .
goto :eof

:format-py
black . && ruff . --fix --show-fixes
goto :eof

:lint-js
npm --prefix .\frontend run lint
goto :eof

:format-js
npm --prefix .\frontend run format
goto :eof

:test
py.test
goto :eof

:test-integration
playwright install --with-deps chromium
set INTEGRATION_TESTS=1
set PWDEBUG=0
set PYTEST_BASE_URL=http://localhost:8080
py.test -sv --liveserver localhost:8080 tests/integration/
goto :eof

:test-integration-debug
playwright install --with-deps chromium
set INTEGRATION_TESTS=1
set PWDEBUG=1
set PYTEST_BASE_URL=http://localhost:8080
py.test -sv --liveserver localhost:8080 tests/integration/
goto :eof

:test-refresh
rmdir /s /q .\tests\data\cassettes
py.test
goto :eof

:test-js
npm --prefix .\frontend run test-windows
goto :eof

:coverage
coverage run -m pytest
coverage html -d coverage_html
echo "Report ready; open ./coverage_html/index.html to view"
goto :eof

:loc
cloc --exclude-dir=migrations,node_modules,public,private,vendor,venv --exclude-ext=json,yaml,svg,toml,ini --vcs=git --counted loc-files.txt .
goto :eof

:startdb
pg_ctl -D %HOMEPATH%\dev\pgdata -l %HOMEPATH%\dev\pgdata\logs\logfile start
goto :eof
