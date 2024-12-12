#!/usr/bin/env bash

python -m gunicorn --worker-class uvicorn.workers.UvicornWorker --reload --access-logfile - --error-logfile - project.asgi:application
