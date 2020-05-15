.PHONY: clean build upload-testpypi upload-pypi
.DEFAULT_GOAL := help
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: ## Remove old artifacts
	rm -rf dist build *.egg-info

build: clean  ## Build python distribution
	python setup.py build
	python setup.py sdist bdist_wheel
	twine check dist/*.tar.gz
	twine check dist/*.whl

upload-testpypi:  ## Upload packages to testpypi
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload-pypi:  ## Upload packages to pypi
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
