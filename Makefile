#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for django project
#
# useful targets:
#   make buld ----------------- build artifacts for production
#   make deploy --------------- deploy service in docker
#   make resetdb -------------- cleanup database and insert data
#   make tests ---------------- run the tests
#   make lint ----------------- source code auto format and checks
#   make docs ----------------- build HTML documentation
#   make watch-docs ----------- starts HTTP sperver to watch documentation with live reload

DOCS = $(CURDIR)/docs
WEB = $(CURDIR)/web
VENV = $(WEB)/env
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_COMPOSE_ARGS =
ENVIRONMENT ?= development
else
ENVIRONMENT ?= production
DOCKER_COMPOSE_ARGS = -f $(ENVIRONMENT).yml
endif
DOCKER_COMPOSE = docker-compose $(DOCKER_COMPOSE_ARGS)
MANAGE = $(DOCKER_COMPOSE) run web python manage.py
WEB_PACKAGE = spec_ibride

export DJANGO_SETTINGS_MODULE = $(WEB_PACKAGE).settings

build:
	@if [ -n "$(DOCKER_HOST)" ]; then echo "Invalid environment"; exit 1; fi
	$(DOCKER_COMPOSE) run static npm run build

deploy:
	@echo Deploy environment: "$(ENVIRONMENT)"
	$(DOCKER_COMPOSE) build
	#$(DOCKER_COMPOSE) stop
	$(DOCKER_COMPOSE) up -d
	$(MANAGE) migrate
	@if [ $(ENVIRONMENT) = 'production' ]; then $(MANAGE) collectstatic -c --noinput; fi

resetdb:
	$(MANAGE) reset_db --noinput
	$(MANAGE) migrate
	cat data/test-photo.csv | $(MANAGE) populatedb -d -

release: build deploy

# Setup environment
env:
	virtualenv $(VENV) --clear
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e web
	$(VENV)/bin/pip install --upgrade -r web/requirements-dev.txt

# Testing
tests:
	$(DOCKER_COMPOSE) run web py.test $(WEB_PACKAGE)

# QA
format:
	$(DOCKER_COMPOSE) run web sh -c 'find ./$(WEB_PACKAGE) -type f -name "*.py" -exec isort --settings-path $$(pwd) {} \;'
	$(DOCKER_COMPOSE) run web pyformat -r -i --exclude _version.py --exclude env ./

loc:
	$(DOCKER_COMPOSE) run web sloccount $(WEB_PACKAGE)

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	$(DOCKER_COMPOSE) run web pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 --exclude _version.py $(WEB_PACKAGE)/

pyflakes:
	$(DOCKER_COMPOSE) run web pyflakes $(WEB_PACKAGE)

docs-lint:
	$(VENV)/bin/doc8 --ignore-path $(DOCS)/_build --max-line-length=120 $(DOCS)

lint: format pep8 pyflakes loc #docs-lint


# Build documentation
docs: docs-db
	. $(VENV)/bin/activate && sphinx-apidoc -f -o $(DOCS) $(WEB_PACKAGE)
	. $(VENV)/bin/activate && $(MAKE) -C $(DOCS) html

docs-db:
	. $(VENV)/bin/activate && $(MANAGE) graph_models -a -g -o $(DOCS)/_static/images/db.svg

docs-watch: docs
	. $(VENV)/bin/activate && sphinx-autobuild -E -a -z $(WEB) -n -b html $(DOCS) $(DOCS)/_build/html



.PHONY: env tests loc pep8 pyflakes format rst-lint lint docs watch-docs
