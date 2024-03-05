#!/usr/bin/env bash

set -x

mypy fastapi_easy_crud --explicit-package-bases
black fastapi_easy_crud --check
isort --check-only fastapi_easy_crud
flake8 fastapi_easy_crud --max-line-length=127
