#!/bin/sh

set -e  
set -x

export PYTHONPATH=$(pwd)

# If a migration name/id is provided, downgrade to that specific migration
# Otherwise, downgrade by 1 revision
if [ -n "$1" ]; then
    alembic downgrade "$1"
else
    alembic downgrade -1
fi