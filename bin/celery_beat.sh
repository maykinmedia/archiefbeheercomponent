#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

mkdir -p celerybeat

echo "Starting celery beat"
celery  --workdir src --app archiefbeheercomponent beat \
    -l $LOGLEVEL \
    -s ../celerybeat/beat
