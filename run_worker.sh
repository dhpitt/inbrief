#!/bin/zsh

celery -A proj purge
celery -A celery_api worker -l INFO



