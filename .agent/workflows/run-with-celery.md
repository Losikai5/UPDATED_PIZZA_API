---
description: How to run the Pizza API with Celery for async email processing
---

# Running Pizza API with Celery

This workflow explains how to start all components of the Pizza API with Celery for asynchronous email processing.

## Prerequisites

1. **Redis Server** - Required for Celery broker and result backend
2. **Virtual Environment** - Activated with all dependencies installed
3. **Environment Variables** - Configured in `.env` file

## Installation Steps

### 1. Install Redis (if not already installed)

**Windows:**
```powershell
# Using Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### 2. Verify Dependencies

Ensure these packages are in your virtual environment:
```powershell
pip install celery[redis] redis asgiref
```

## Running the Application

You need to run **THREE** separate processes:

### Terminal 1: Start Redis Server

```powershell
# Windows (if installed via Chocolatey)
redis-server

# Or if using WSL
wsl redis-server

# Linux/Mac
redis-server
```

**Verify Redis is running:**
```powershell
redis-cli ping
# Should return: PONG
```

### Terminal 2: Start Celery Worker

```powershell
# Activate virtual environment
.\\venv\\Scripts\\Activate.ps1

# Start Celery worker (Option 1: Using script)
python run_celery.py

# OR (Option 2: Direct command)
celery -A src.celery_task.celery_app worker --loglevel=info --pool=solo
```

**Expected output:**
```
[INFO] celery@hostname ready.
[INFO] Registered tasks:
    - send_email_task
```

### Terminal 3: Start FastAPI Application

```powershell
# Activate virtual environment
.\\venv\\Scripts\\Activate.ps1

# Start FastAPI server
uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

## Testing Celery Integration

### 1. Test Signup Endpoint

```powershell
curl -X POST "http://localhost:8000/api/v2/auth/signup" `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "password123",
    "role": "user",
    "is_verified": false
  }'
```

**Expected response:**
```json
{
  "message": "User created successfully. Please check your email to verify your account.",
  "user": {...}
}
```

**Check Celery worker logs** - You should see:
```
[INFO] Task send_email_task[...] received
[INFO] Sending email to ['test@example.com'] with subject: Welcome to Our Service - Verify Your Email
[INFO] Email sent successfully to ['test@example.com']
[INFO] Task send_email_task[...] succeeded
```

### 2. Test Password Reset

```powershell
curl -X POST "http://localhost:8000/api/v2/auth/password-reset-request" `
  -H "Content-Type: application/json" `
  -d '{"email": "test@example.com"}'
```

## Monitoring Celery Tasks

### Using Flower (Optional)

Install Flower for web-based monitoring:
```powershell
pip install flower

# Start Flower
celery -A src.celery_task.celery_app flower
```

Access at: `http://localhost:5555`

### Using Redis CLI

Check queued tasks:
```powershell
redis-cli
> LLEN celery
> KEYS *
```

## Troubleshooting

### Issue: Celery worker won't start

**Solution:** Ensure Redis is running first
```powershell
redis-cli ping
```

### Issue: Tasks not being processed

**Solution:** Check Redis connection in `.env`
```
REDIS_URL=redis://localhost:6379/0
```

### Issue: Email not sending

**Solution:** Check email configuration in `.env`
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Pizza API
```

### Issue: Windows compatibility errors

**Solution:** Use `--pool=solo` flag for Celery worker
```powershell
celery -A src.celery_task.celery_app worker --loglevel=info --pool=solo
```

## Stopping the Application

1. **Stop FastAPI** - Press `Ctrl+C` in Terminal 3
2. **Stop Celery Worker** - Press `Ctrl+C` in Terminal 2
3. **Stop Redis** - Press `Ctrl+C` in Terminal 1

## Production Deployment

For production, consider:

1. **Supervisor/systemd** - Auto-restart workers
2. **Multiple workers** - Scale horizontally
3. **Monitoring** - Use Flower or Prometheus
4. **Redis persistence** - Configure AOF/RDB
5. **Task routing** - Separate queues for different task types

## Environment Variables

Required in `.env`:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=Pizza API

# Domain
DOMAIN=localhost:8000
```
