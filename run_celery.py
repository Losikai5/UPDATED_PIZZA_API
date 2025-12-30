"""
Celery Worker Startup Script for Pizza API

This script starts a Celery worker to process background tasks,
primarily for sending emails asynchronously.

Usage:
    python run_celery.py

Or directly with Celery:
    celery -A src.celery_task.celery_app worker --loglevel=info
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Celery app
from src.celery_task import celery_app

if __name__ == '__main__':
    # Start Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',  # Number of worker processes
        '--pool=solo',  # Use solo pool for Windows compatibility
        '--task-events',  # Enable task events for monitoring
        '--without-gossip',  # Disable gossip for better performance
        '--without-mingle',  # Disable mingle for faster startup
        '--without-heartbeat',  # Disable heartbeat for simplicity
    ])
