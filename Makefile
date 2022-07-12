.PHONY: sync-dev build build-pex dev docs loc lint format lint-py format-py lint-js format-js test test-integration test-integration-debug test-refresh test-js coverage
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

sync-dev:  ## Sync dev environment after code checkout
	python -m pip install -U pip
	pip install -r requirements/dev.txt
	yarn --cwd frontend
	manage.py migrate
	manage.py recreate_views

build:  ## build hawc package
	npm --prefix ./frontend run build
	manage.py set_git_commit
	rm -rf build/ dist/
	python setup.py bdist_wheel

build-pex: build ## build pex
	cd requirements; pex \
		-r production.txt \
		-c manage.py \
		-o ../dist/hawc.pex \
		--python-shebang='#!/usr/bin/env python'  \
		--disable-cache \
		--ignore-errors \
		../dist/hawc-0.1-py3-none-any.whl

dev: ## Start development environment
	@if [ -a ./bin/dev.local.sh ]; then \
		./bin/dev.local.sh; \
	else \
		./bin/dev.sh; \
	fi;

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

docs: ## Generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

loc: ## Generate lines of code report
	@cloc \
		--exclude-dir=migrations,node_modules,public,private,vendor,venv \
		--exclude-ext=json,yaml,svg,toml,ini \
		--vcs=git \
		--counted loc-files.txt \
		.

lint: lint-py lint-js  ## Check for javascript/python for linting issues

format: format-py format-js  ## Modify javascript/python code

lint-py:  ## Check for python formatting issues via black & flake8
	@black . --check && flake8 .

format-py:  ## Modify python code using black & show flake8 issues
	@black . && isort . && flake8 .

lint-js:  ## Check for javascript formatting issues
	@npm --prefix ./frontend run lint

format-js:  ## Modify javascript code if possible using linters/formatters
	@npm --prefix ./frontend run format

test:  ## Run python tests
	@py.test

test-integration:  ## Run integration tests (requires `npm run start`)
	@playwright install --with-deps chromium
	@HAWC_INTEGRATION_TESTS=1 py.test -sv tests/frontend/integration/

test-integration-debug:  ## Run integration tests in debug mode (requires npm run start)
	@playwright install --with-deps chromium
	@HAWC_INTEGRATION_TESTS=1 PWDEBUG=1 py.test -sv tests/frontend/integration/

test-refresh: ## Removes mock requests and runs python tests
	rm -rf tests/data/cassettes
	@py.test

test-js:  ## Run javascript tests
	@npm --prefix ./frontend run test

coverage:  ## Run coverage and create html report
	coverage run -m pytest
	coverage html -d coverage_html
	@echo "Report ready: ./coverage_html/index.html"
