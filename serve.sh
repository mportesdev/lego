#!/usr/bin/env bash

python -m gunicorn project.asgi:application
