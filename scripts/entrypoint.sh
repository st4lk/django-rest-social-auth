#!/usr/bin/env bash

PROJECT_PATH=/django_rest_social_auth

# create virtualenv if it doesn't exist
python -m venv /${PROJECT_PATH}/venv
. ${PROJECT_PATH}/venv/bin/activate

export PYENV_ROOT="${PROJECT_PATH}/.pyenv"
export PATH="${PROJECT_PATH}/.pyenv/bin:${PATH}"

cd ${PROJECT_PATH}
gosu appuser $1
