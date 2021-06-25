#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:8000 --worker-class 'uvicorn.workers.UvicornWorker' --workers 4 server:app --daemon