MTA_SERVER  := mta-server
MTA_MONITOR := mta-monitor
PKG_VERSION := $(shell poetry version | awk '{print $$2}')

.PHONY: docker up version help
.DEFAULT_GOAL := help


docker:  ## Build the docker images.
	docker build -f Dockerfile.main -t ${MTA_SERVER}:latest .
	docker build -f Dockerfile.monitor -t ${MTA_MONITOR}:latest .

up: docker  ## Run docker-compose up.
	docker-compose -f docker-compose.yaml up

version:  ## Print the application version
	@echo "${PKG_VERSION}"

help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
