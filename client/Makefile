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
	rm -rf *.egg-info build dist

build: clean  ## Build python distribution
	flit build

upload-testpypi:  ## Upload packages to testpypi
	flit publish --repository testpypi

upload-pypi:  ## Upload packages to pypi
	flit publish
