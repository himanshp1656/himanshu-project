#!/bin/bash

echo "Applying database migrations..."
python3 manage.py migrate

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting service: $@"
exec "$@"
