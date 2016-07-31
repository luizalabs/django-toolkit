.PHONY: help

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check:  ## Run static code checks
	@flake8 .
	@isort --check

test:  ## Run unit tests
	@py.test -x tests/

coverage:  ## Run unit tests and generate code coverage report
	@py.test -x --cov django_toolkit/ --cov-report=xml --cov-report=term-missing tests/
