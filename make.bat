@ECHO off

if "%~1" == "" goto :help
if /I %1 == help goto :help
if /I %1 == build goto :build
if /I %1 == lint goto :lint
if /I %1 == format goto :format
if /I %1 == lint-py goto :lint-py
if /I %1 == format-py goto :format-py
if /I %1 == lint-js goto :lint-js
if /I %1 == format-js goto :format-js
if /I %1 == test goto :test
if /I %1 == test-integration goto :test-integration
if /I %1 == test-refresh goto :test-refresh
if /I %1 == coverage goto :coverage
if /I %1 == loc goto :loc
goto :help

:build
del /f /q .\build .\dist
npm --prefix .\frontend run build
manage.py set_git_commit
manage.py build_hawc_bundle
goto :eof

:help
echo.Please use `make ^<target^>` where ^<target^> is one of
echo.  build             build python application
echo.  test              run python tests
echo.  test-integration  run integration tests (requires npm run start)
echo.  test-refresh      removes mock requests and runs python tests
echo.  coverage          run coverage and create html report
echo.  lint              perform both lint-py and lint-js
echo.  format            perform both format-py and lint-js
echo.  lint-py           check for pytho formatting issues via black and flake8
echo.  format-py         modify python code using black and show flake8 issues
echo.  lint-js           check for javascript formatting issues
echo.  format-js         modify javascript code if possible using linters and formatters
echo.  loc               generate lines of code report
goto :eof

:lint
black . --check && flake8 .
npm --prefix .\frontend run lint
goto :eof

:format
black . && isort -rc -y && flake8 .
npm --prefix .\frontend run format
goto :eof

:lint-py
black . --check && flake8 .
goto :eof

:format-py
black . && isort -rc -y && flake8 .
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
HAWC_INTEGRATION_TESTS=1 SHOW_BROWSER=1 BROWSER="firefox" py.test -s tests/frontend/integration/
goto :eof

:test-refresh
rmdir /s /q .\tests\data\cassettes
py.test
goto :eof

:coverage
coverage run -m pytest
coverage html -d coverage_html
echo "Report ready; open ./coverage_html/index.html to view"
goto :eof

:loc
cloc --exclude-dir=migrations,node_modules,public,private,vendor,venv --exclude-ext=json,yaml,svg,toml,ini --vcs=git --counted loc-files.txt .
goto :eof
