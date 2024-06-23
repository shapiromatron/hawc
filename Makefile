.PHONY: sync-dev build dev docs loc lint format lint-py format-py lint-js format-js test test-integration test-integration-debug test-refresh test-js coverage
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
	python -m pip install -U pip uv
	uv pip install -e ".[dev,docs]"
	uv pip install -e client
	yarn --cwd frontend
	python manage.py migrate
	python manage.py recreate_views

build:  ## build hawc package
	npm --prefix ./frontend run build
	python manage.py set_git_commit
	flit build

dev: ## Start development environment
	@if [ -a ./bin/dev.local.sh ]; then \
		./bin/dev.local.sh; \
	else \
		./bin/dev.sh; \
	fi;

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

docs: ## Build documentation
	cd docs; mkdocs build --strict

docs-serve: ## Generate documentation
	cd docs; mkdocs serve -a localhost:8010

loc: ## Generate lines of code report
	@cloc \
		--exclude-dir=migrations,node_modules,public,private,vendor,venv \
		--exclude-ext=json,yaml,svg,toml,ini \
		--vcs=git \
		--counted loc-files.txt \
		--md \
		.

lint: lint-py lint-js  ## Check formatting issues

format: format-py format-js format-html ## Fix formatting issues where possible

lint-py:  ## Check python formatting issues
	@ruff format . --check && ruff check .

format-py:  ## Fix python formatting issues where possible
	@ruff format . && ruff check . --fix --show-fixes

lint-js:  ## Check javascript formatting issues
	@npm --prefix ./frontend run lint

format-js:  ## Fix javascript formatting issues where possible
	@npm --prefix ./frontend run format

lint-html:  ## Check HTML formatting issues where possible
	@djhtml --tabwidth 2 --check hawc/

format-html:  ## Fix HTML formatting issues where possible
	@djhtml --tabwidth 2 hawc/

test:  ## Run python tests
	@py.test

test-integration:  ## Run integration tests (requires `npm run start`)
	@playwright install --with-deps chromium
	@INTEGRATION_TESTS=1 py.test -sv tests/integration/

test-integration-debug:  ## Run integration tests in debug mode (requires npm run start)
	@playwright install --with-deps chromium
	@INTEGRATION_TESTS=1 PWDEBUG=1 py.test -sv tests/integration/

test-refresh: ## Removes mock requests and runs python tests
	rm -rf tests/data/cassettes
	@py.test

test-js:  ## Run javascript tests
	@npm --prefix ./frontend run test

coverage:  ## Run coverage and create html report
	coverage run -m pytest
	coverage html -d coverage_html
	@echo "Report ready: ./coverage_html/index.html"
