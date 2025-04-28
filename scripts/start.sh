#!/bin/sh
set -e  # Stop script if a command fails
set -x  # Print commands before executing them

export PYTHONPATH=$(pwd)

echo "Running Database Initialization..."
python app/backend_pre_start.py

echo "Running Alembic Migrations..."
alembic upgrade head

echo "Running Seeders..."
python app/initial_data.py

echo "Database setup complete. Proceeding to application startup..."
