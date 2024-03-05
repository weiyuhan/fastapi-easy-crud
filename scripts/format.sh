#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place fastapi_easy_crud --exclude=__init__.py
black fastapi_easy_crud
isort fastapi_easy_crud

