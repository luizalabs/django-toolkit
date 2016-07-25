.PHONY: help

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check:  ## Run static code checks
	@flake8 .
	@isort --check

test:  ## Run unit tests
	@py.test -x tests/
