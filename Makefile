.PHONY: dev docs servedocs lint format lint-py format-py lint-js format-js test
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

build:  ## build python application
	rm -rf build/ dist/
	npm --prefix ./frontend run build
	manage.py set_git_commit
	manage.py build_hawc_bundle

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

servedocs: docs ## Compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .


lint: lint-py lint-js  ## Check for javascript/python for linting issues

format: format-py format-js  ## Modify javascript/python code

lint-py:  ## Check for python formatting issues via black & flake8
	@black . --check && flake8 .

format-py:  ## Modify python code using black & show flake8 issues
	@black . && isort -rc -y && flake8 .

lint-js:  ## Check for javascript formatting issues
	@npm --prefix ./frontend run lint

format-js:  ## Modify javascript code if possible using linters/formatters
	@npm --prefix ./frontend run format

test:  ## Run python tests
	@py.test

flynt:  ## Run flynt (optional) using preferred config
	@flynt --verbose --line_length=120 hawc/
