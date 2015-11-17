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
SRC=$(CURDIR)/src
VENV=$(CURDIR)/env
MANAGE=$(SRC)/manage.py


# Setup environment
env:
	virtualenv $(VENV) --clear
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e .
	$(VENV)/bin/pip install --upgrade -r requirements/development.txt


# Testing
tests:
	$(VENV)/bin/py.test $(SRC)


# QA
format:
	find $(SRC) -type f -name '*.py' -exec isort --settings-path $(CURDIR) {} \;
	pyformat -r -i --exclude _version.py $(SRC)/ setup.py

loc:
	sloccount $(SRC)

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests"
	@echo "#############################################"
	-pep8 -r --ignore=E501,E221,W291,W391,E302,E251,E203,W293,E231,E303,E201,E225,E261,E241 --exclude _version.py $(SRC)/

pyflakes:
	pyflakes $(SRC)

docs-lint:
	$(VENV)/bin/doc8 --ignore-path $(DOCS)/_build --max-line-length=120 $(DOCS)

lint: format pep8 pyflakes loc docs-lint


# Build documentation
docs: docs-db
	. $(VENV)/bin/activate && sphinx-apidoc -f -o $(DOCS) $(SRC)/spec_ibride
	. $(VENV)/bin/activate && $(MAKE) -C $(DOCS) html

docs-db:
	. $(VENV)/bin/activate && $(MANAGE) graph_models -a -g -o $(DOCS)/_static/images/db.svg

docs-watch: docs
	. $(VENV)/bin/activate && sphinx-autobuild -E -a -z $(SRC) -n -b html $(DOCS) $(DOCS)/_build/html


.PHONY: dev tests loc pep8 pyflakes format rst-lint lint docs watch-docs
