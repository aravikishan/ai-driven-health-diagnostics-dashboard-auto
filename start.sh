#!/bin/bash
set -e
echo "Starting AI-Driven Health Diagnostics Dashboard..."
uvicorn app:app --host 0.0.0.0 --port 9110 --workers 1
