#!/bin/bash
set -e
echo "Starting Real-Time Cryptocurrency Portfolio Tracker..."
uvicorn app:app --host 0.0.0.0 --port 9051 --workers 1
