.PHONY: dev-setup fmt lint syntaxcheck check test test-pytest test-tox upload

VENV := .env
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV_PYTHON) -m pip --isolated
PIP_CLEAN_ENV := PIP_CONFIG_FILE=/dev/null PIP_USER=0
PY_FILES := dsenv.py tests/test_dsenv.py

$(VENV)/bin/python:
	python -m venv $(VENV)

$(VENV)/.dev-installed: requirements-dev.txt | $(VENV)/bin/python
	$(VENV_PIP) install -r requirements-dev.txt
	touch $(VENV)/.dev-installed

dev-setup: $(VENV)/.dev-installed

fmt: $(VENV)/.dev-installed
	$(VENV)/bin/isort $(PY_FILES)
	$(VENV)/bin/black $(PY_FILES)

lint: $(VENV)/.dev-installed
	$(VENV)/bin/isort --check-only $(PY_FILES)
	$(VENV)/bin/black --check $(PY_FILES)

syntaxcheck: $(VENV)/.dev-installed
	$(VENV_PYTHON) -m py_compile $(PY_FILES)

test-pytest: $(VENV)/.dev-installed
	PYTHONPATH=. $(VENV)/bin/pytest -q

test-tox:
	tox

test: test-pytest

check: syntaxcheck lint test-pytest

upload: $(VENV)/.dev-installed
	$(PIP_CLEAN_ENV) $(VENV_PYTHON) -m build
	$(VENV)/bin/twine upload dist/*
