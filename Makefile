#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for django project
#
# useful targets:
#   make env ------------------ install development requirements
#   make tests ---------------- run the tests
#   make lint ----------------- source code auto format and checks
#   make docs ----------------- build HTML documentation
#   make watch-docs ----------- starts HTTP sperver to watch documentation with live reload

DOCS=$(CURDIR)/docs
WEB=$(CURDIR)/web
VENV=$(WEB)/env
ifeq ($(strip $(DOCKER_HOST)),)
DOCKER_COMPOSE_ARGS=
ENVIRONMENT=?development
else
DOCKER_COMPOSE_ARGS=-f production.yml
ENVIRONMENT=?production
endif
DOCKER_COMPOSE=docker-compose $(DOCKER_COMPOSE_ARGS)
MANAGE=$(DOCKER_COMPOSE) run web python manage.py

export DJANGO_SETTINGS_MODULE = spec_ibride.settings

build:
	@if [ -n "$(DOCKER_HOST)" ]; then echo "Invalid environment"; exit 1; fi
	$(DOCKER_COMPOSE) run static npm run build

deploy:
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
	$(VENV)/bin/py.test $(WEB)

# QA
format:
	find $(WEB) -type f -name '*.py' -exec isort --settings-path $(CURDIR) {} \;
	pyformat -r -i --exclude _version.py $(WEB)/

loc:
	sloccount $(WEB)

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 --exclude _version.py $(WEB)/

pyflakes:
	pyflakes $(WEB)

docs-lint:
	$(VENV)/bin/doc8 --ignore-path $(DOCS)/_build --max-line-length=120 $(DOCS)

lint: format pep8 pyflakes loc docs-lint


# Build documentation
docs: docs-db
	. $(VENV)/bin/activate && sphinx-apidoc -f -o $(DOCS) $(WEB)/spec_ibride
	. $(VENV)/bin/activate && $(MAKE) -C $(DOCS) html

docs-db:
	. $(VENV)/bin/activate && $(MANAGE) graph_models -a -g -o $(DOCS)/_static/images/db.svg

docs-watch: docs
	. $(VENV)/bin/activate && sphinx-autobuild -E -a -z $(WEB) -n -b html $(DOCS) $(DOCS)/_build/html



.PHONY: env tests loc pep8 pyflakes format rst-lint lint docs watch-docs
