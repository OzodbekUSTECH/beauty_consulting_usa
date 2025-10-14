#!/bin/bash

# Run Alembic migrations
alembic upgrade head

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT