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
goto :help

:build
del /f /q .\build .\dist
npm --prefix .\frontend run build
manage.py set_git_commit
manage.py build_hawc_bundle
goto :eof

:help
echo.Please use `make ^<target^>` where ^<target^> is one of
echo.  build      build python application
echo.  test       run python tests
echo.  lint       perform both lint-py and lint-js
echo.  format     perform both format-py and lint-js
echo.  lint-py    check for pytho formatting issues via black and flake8
echo.  format-py  modify python code using black and show flake8 issues
echo.  lint-js    check for javascript formatting issues
echo.  format-js  modify javascript code if possible using linters and formatters
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
