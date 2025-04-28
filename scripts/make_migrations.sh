#!/bin/sh

set -e  
set -x

export PYTHONPATH=$(pwd)

alembic revision --autogenerate -m "$1"