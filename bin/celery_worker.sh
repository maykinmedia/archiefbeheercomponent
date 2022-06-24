#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

echo "Starting celery worker"
celery --workdir src --app archiefbeheercomponent.celery worker \
    -l $LOGLEVEL \
    -O fair \
