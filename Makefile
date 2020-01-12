.PHONY: run all test test_tox shell run-example native-test native-test-tox

PROJECT_PATH = /django_rest_social_auth
PORT ?= 8000

# ---------------------------
# Commands for running docker
# ---------------------------

all: run-example

build: .build
.build: Dockerfile scripts/*
	docker build -t st4lk/django-rest-social-auth .
	touch $@

rebuild:
	rm .build
	$(MAKE) build

run: build
	docker run -it --rm --name django-rest-social-auth \
		-p $(PORT):$(PORT) \
		-v $(PWD):$(PROJECT_PATH)/ \
		st4lk/django-rest-social-auth "$(COMMAND)"

run-example:
	@COMMAND='make native-run-example' $(MAKE) run

test:
	@COMMAND='make native-test' $(MAKE) run

test-tox:
	@COMMAND='make native-test-tox' $(MAKE) run

shell:
	@COMMAND='bash' $(MAKE) run

# ------------------------
# Commands to run natively
# ------------------------

native-install: .install
.install: requirements.txt
	pip install -r requirements.txt
	touch $@

native-install-test: .install-test
.install-test: requirements_test.txt
	pip install -r requirements_test.txt
	touch $@

native-install-optional: .install-optional
.install-optional: requirements_optional.txt
	pip install -r requirements_optional.txt
	touch $@

native-install-all: native-install native-install-test native-install-optional

native-migrate: native-install-all
	PYTHONPATH='.' python example_project/manage.py migrate

native-run-example: native-migrate
	PYTHONPATH='.' python example_project/manage.py runsslserver 0.0.0.0:$(PORT)

native-clean:
	find . -path ./venv -prune | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

native-test: native-install-all native-clean
	PYTHONPATH='example_project/' python -m pytest -Wignore $(TEST_ARGS)

native-install-python-versions: .install-python-versions
.install-python-versions: tox.ini
	curl https://pyenv.run | PYENV_ROOT=$(PROJECT_PATH)/.pyenv bash || echo '-- pyenv already setup, skipping --\n'
	PYENV_ROOT=$(PROJECT_PATH)/.pyenv $(PROJECT_PATH)/.pyenv/bin/pyenv install -s 2.7.17
	PYENV_ROOT=$(PROJECT_PATH)/.pyenv $(PROJECT_PATH)/.pyenv/bin/pyenv install -s 3.5.9
	PYENV_ROOT=$(PROJECT_PATH)/.pyenv $(PROJECT_PATH)/.pyenv/bin/pyenv install -s 3.6.10
	PYENV_ROOT=$(PROJECT_PATH)/.pyenv $(PROJECT_PATH)/.pyenv/bin/pyenv install -s 3.8.1
	pyenv global system 2.7.17 3.5.9 3.6.10 3.8.1
	touch $@

native-test-tox: native-install-python-versions native-clean
	pip install tox tox-pyenv
	tox
