#!/bin/sh -e
set -x

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive  --force-single-line-imports --apply fastapi_easy_crud
sh ./scripts/format.sh
