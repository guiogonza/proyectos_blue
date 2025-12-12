#!/bin/bash
# run_api.sh
cd /app
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
