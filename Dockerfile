# Base image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies and `supervisord`
RUN apk add --no-cache gcc libpq libpq-dev musl-dev supervisor

# Copy dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
	mkdir -p /tmp

# TODO: uncomment this when we have a background task to run
# COPY ./_celery /app/_celery

# Copy application source code
COPY ./scripts /app/scripts
COPY ./gunicorn.conf.py /app/gunicorn.conf.py
COPY ./alembic.ini /app/alembic.ini
COPY ./app /app/app
COPY ./supervisord.conf /app/supervisord.conf

# Make scripts executable
RUN chmod +x /app/scripts/start.sh

# Run `start.sh` first, then launch `supervisord`
CMD ["/bin/sh", "-c", "/app/scripts/start.sh && supervisord -c /app/supervisord.conf"]
