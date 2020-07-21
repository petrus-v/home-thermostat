.PHONY: help
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

init: ## Setup dev env pulling and building docker images for testing purpose
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --parallel --pull

define setup_db
	@echo Setup Database for $(1) compose file
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.$(1).yml \
		up -d db
	$(call wait_db)
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.$(1).yml \
		run \
			--rm \
			--entrypoint "" \
			backend bash -c "pip install -e . && anyblok_createdb -c app.$(1).cfg --with-demo || anyblok_updatedb -c app.$(1).cfg"
endef

setup-dev:  ## Create or update database that will be ready to run unit tests (with demo data)
	 $(call setup_db,"dev")

setup-integration:  ## Create or update database that will be ready to run integrations tests (with demo data)
	 $(call setup_db,"integration")

psql-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db psql --user iot iot

psql-integration:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db psql --user iot iot_integration

run-dev: ## Locally run the application
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

run:  ## running as production (using docker-compose.override.yaml if present)
	docker-compose up -d

build:
	docker-compose -f docker-compose.yml -f docker-compose.release.yml build --parallel

test: test-unit-backend test-unit-frontend  ## Launching unit tests

test-unit-backend: ## Launch backend unit tests only, use `PYTEST_PARAMS="--lf" make test-unit-backend` to launch last failed tests only)
	$(call wait_db)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend test PYTEST_PARAMS="$(PYTEST_PARAMS)"

test-unit-frontend:  ## Launch frontend unit tests only
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm frontend npm run test:unit

test-unit-frontend-update-snapshot:  ## Launch frontend unit tests update snapshots
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm frontend npm run test:unit -- -u

npm-frontend:  ## launch npm commands, ie make npm-frontend args="update --save-dev"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm frontend npm $(args)


test-integration: build test-integration-build setup-integration test-integration-boot test-integration-run ## Launch integration tests.

test-integration-build:
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.integration.yml \
		build integration-test

test-integration-boot: # Only boot integration tests container
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.integration.yml \
		up -d \
			selenium-hub \
			chrome \
			firefox \
			backend \
			frontend

test-integration-run: # Only run integration tests (without building images nor setup env)
	$(call wait_frontend)
	$(call wait_backend)
	$(call wait_selenium)
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.integration.yml \
		run --rm integration-test

logs: ## display app logs
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.integration.yml \
		logs --tail 100 -f

ps: ## docker-compose ps using integration.yml
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose.integration.yml \
		ps

clean: ## Clean cache files, docker containers and docker volumes
	docker-compose -f docker-compose.yml -f docker-compose.integration.yml down -v --remove-orphans || /bin/true
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans || /bin/true
	docker-compose -f docker-compose.yml down -v --remove-orphans || /bin/true
	rm -rf frontend/node_modules
	rm -fr build/
	rm -fr dist/
	rm -fr bdd-tests/screenshot/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

lint: ## check style with flake8
	pre-commit install --install-hooks
	pre-commit run --all-files --show-diff-on-failure


define wait_db
	docker run --rm \
		-v ${PWD}/wait-for-it.sh:/tmp/wait-for-it.sh \
		--network iot_internal \
		python:3 \
		/tmp/wait-for-it.sh db:5432 -s -t 30 -- echo Postgresql is ready \
	|| (docker-compose -f docker-compose.yml logs --tail 100 db ; echo "Postresql wasn't ready in the given time"; exit 1)
endef

define wait_frontend
	docker run --rm \
		-v ${PWD}/wait-for-it.sh:/tmp/wait-for-it.sh \
		--network iot_internal \
		python:3 \
		/tmp/wait-for-it.sh enrj.local:80 -s -t 30 -- echo "frontend is ready" \
	|| (docker-compose -f docker-compose.yml -f docker-compose.integration.yml logs --tail 100; echo "frontend wasn't ready in the given time"; exit 1)
endef

define wait_backend
	docker run --rm \
		-v ${PWD}/wait-for-it.sh:/tmp/wait-for-it.sh \
		--network iot_internal \
		python:3 \
		/tmp/wait-for-it.sh backend:5000 -s -t 30 -- echo "backend is ready" \
	|| (docker-compose -f docker-compose.yml -f docker-compose.integration.yml logs --tail 100 backend ; echo "backend wasn't ready in the given time"; exit 1)
endef

define wait_selenium
	docker run --rm \
		-v ${PWD}/wait-for-it.sh:/tmp/wait-for-it.sh \
		--network iot_internal \
		python:3 \
		/tmp/wait-for-it.sh selenium-hub:4444 -s -t 60 -- echo "selenium is ready" \
		|| (docker-compose -f docker-compose.yml -f docker-compose.integration.yml logs --tail 100 selenium-hub ; echo "selenium wasn't ready in the given time"; exit 1)
	sleep 2s
	docker-compose -f docker-compose.yml -f docker-compose.integration.yml exec -T \
		selenium-hub /opt/bin/check-grid.sh --host selenium-hub --port 4444 \
		|| (docker-compose -f docker-compose.yml -f docker-compose.integration.yml logs --tail 100 selenium-hub firefox chrome ; echo "selenium status wasn't ready (green)"; exit 1)
endef
