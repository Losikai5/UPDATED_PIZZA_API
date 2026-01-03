# 🚀 Render Deployment Guide for Pizza API

## 📋 Prerequisites
- GitHub repository with your code
- Render account (free tier works)
- Gmail account for email functionality

---

## 🔧 Step 1: Fix Configuration Issues

✅ **Already Fixed:**
- Updated `src/config.py` to work without `.env` file in production
- Pydantic Settings now loads from system environment variables

---

## 🗄️ Step 2: Create PostgreSQL Database on Render

1. **Go to Render Dashboard** → Click "New +" → Select "PostgreSQL"
2. **Configure Database:**
   - **Name:** `pizza-db`
   - **Database:** `pizza_db`
   - **User:** `pizza_user`
   - **Region:** Choose closest to you
   - **Plan:** Free
3. **Click "Create Database"**
4. **Copy the Internal Database URL** (starts with `postgresql://`)

---

## 🔴 Step 3: Create Redis Instance on Render

1. **Go to Render Dashboard** → Click "New +" → Select "Redis"
2. **Configure Redis:**
   - **Name:** `pizza-redis`
   - **Region:** Same as database
   - **Plan:** Free
3. **Click "Create Redis"**
4. **Copy the Internal Redis URL** (starts with `redis://`)

---

## 🌐 Step 4: Create Web Service

1. **Go to Render Dashboard** → Click "New +" → Select "Web Service"
2. **Connect Your GitHub Repository**
3. **Configure Web Service:**

### Basic Settings:
- **Name:** `pizza-api`
- **Region:** Same as database and Redis
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave empty
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && alembic upgrade head
  ```
- **Start Command:**
  ```bash
  uvicorn src:app --host 0.0.0.0 --port $PORT
  ```

### Environment Variables:
Click "Advanced" → Add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | Paste Internal Database URL from Step 2 | Must start with `postgresql+asyncpg://` |
| `REDIS_URL` | Paste Internal Redis URL from Step 3 | |
| `JWT_SECRET` | Generate random string | Use: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | `HS256` | |
| `DOMAIN` | Your Render URL | e.g., `pizza-api.onrender.com` |
| `MAIL_USERNAME` | Your Gmail username | Without @gmail.com |
| `MAIL_PASSWORD` | Gmail App Password | See Step 5 |
| `MAIL_FROM` | Your Gmail address | e.g., `you@gmail.com` |
| `MAIL_SERVER` | `smtp.gmail.com` | |
| `MAIL_PORT` | `587` | |
| `MAIL_FROM_NAME` | Your name | e.g., `Pizza Shop` |
| `MAIL_STARTTLS` | `True` | |
| `MAIL_SSL_TLS` | `False` | |
| `USE_CREDENTIALS` | `True` | |
| `VALIDATE_CERTS` | `True` | |

### ⚠️ CRITICAL: Fix DATABASE_URL
Render provides `postgresql://` but your app needs `postgresql+asyncpg://`

**Option 1: Manual Fix (Recommended)**
In the `DATABASE_URL` environment variable, change:
```
postgresql://user:pass@host/db
```
to:
```
postgresql+asyncpg://user:pass@host/db
```

**Option 2: Auto-fix in code**
Add this to `src/db/main.py` before using the URL:
```python
from src.config import Config

# Fix DATABASE_URL for asyncpg
database_url = Config.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
```

4. **Click "Create Web Service"**

---

## 📧 Step 5: Setup Gmail App Password

1. **Go to:** https://myaccount.google.com/security
2. **Enable 2-Step Verification** (if not already enabled)
3. **Go to:** https://myaccount.google.com/apppasswords
4. **Create App Password:**
   - App: Mail
   - Device: Other (Custom name) → "Pizza API"
5. **Copy the 16-character password** (no spaces)
6. **Use this as `MAIL_PASSWORD`** in Render environment variables

---

## 🐛 Common Issues & Solutions

### Issue 1: Database Connection Failed
**Error:** `connection to server failed`

**Solution:**
- Ensure `DATABASE_URL` uses `postgresql+asyncpg://` (not just `postgresql://`)
- Use the **Internal Database URL** from Render (not External)
- Check database and web service are in the same region

### Issue 2: Redis Connection Failed
**Error:** `Error connecting to Redis`

**Solution:**
- Use the **Internal Redis URL** from Render
- Ensure Redis instance is running
- Check both services are in same region

### Issue 3: Email Not Sending
**Error:** `Authentication failed` or `SMTPAuthenticationError`

**Solution:**
- Use Gmail **App Password**, not regular password
- Ensure 2-Step Verification is enabled on Gmail
- Check `MAIL_USERNAME` doesn't include `@gmail.com`

### Issue 4: Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
- Ensure `requirements.txt` includes all dependencies
- Check start command uses `src:app` not `src.main:app`

### Issue 5: Alembic Migration Fails
**Error:** `alembic.util.exc.CommandError`

**Solution:**
- Ensure `alembic.ini` has correct `sqlalchemy.url` or uses env variable
- Check `migrations/env.py` uses `Config.DATABASE_URL`
- Run migrations manually: `alembic upgrade head`

---

## 🧪 Step 6: Verify Deployment

1. **Check Build Logs:**
   - Should see "Installing dependencies..."
   - Should see "Running database migrations..."
   - Should see "Build completed successfully!"

2. **Check Deploy Logs:**
   - Should see ">>>>starting.........."
   - Should see "Application startup complete"

3. **Test API:**
   ```bash
   # Health check
   curl https://your-app.onrender.com/docs
   
   # Should see FastAPI Swagger UI
   ```

4. **Test Endpoints:**
   - Go to: `https://your-app.onrender.com/docs`
   - Try the `/api/v2/auth/signup` endpoint
   - Check if email verification is sent

---

## 🔄 Step 7: Setup Celery Worker (Optional)

For async email processing, you need a separate worker:

1. **Create Background Worker:**
   - Dashboard → "New +" → "Background Worker"
   - **Name:** `pizza-celery-worker`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `celery -A src.celery_task worker --loglevel=info`
   - **Environment Variables:** Same as web service

2. **Note:** Free tier may not support background workers. Consider:
   - Using synchronous email sending for free tier
   - Upgrading to paid plan for Celery workers

---

## 📝 Environment Variables Checklist

Before deploying, ensure you have:

- [ ] `DATABASE_URL` (with `postgresql+asyncpg://`)
- [ ] `REDIS_URL`
- [ ] `JWT_SECRET` (random 32+ character string)
- [ ] `JWT_ALGORITHM` (HS256)
- [ ] `DOMAIN` (your Render URL)
- [ ] `MAIL_USERNAME`
- [ ] `MAIL_PASSWORD` (App Password, not regular password)
- [ ] `MAIL_FROM`
- [ ] `MAIL_SERVER` (smtp.gmail.com)
- [ ] `MAIL_PORT` (587)
- [ ] `MAIL_FROM_NAME`

---

## 🎯 Quick Deploy Checklist

1. ✅ Fix `config.py` (already done)
2. ✅ Create PostgreSQL database on Render
3. ✅ Create Redis instance on Render
4. ✅ Create web service on Render
5. ✅ Set all environment variables
6. ✅ Fix `DATABASE_URL` to use `postgresql+asyncpg://`
7. ✅ Setup Gmail App Password
8. ✅ Deploy and check logs
9. ✅ Test API endpoints

---

## 🆘 Still Having Issues?

1. **Check Render Logs:**
   - Dashboard → Your Service → "Logs" tab
   - Look for error messages

2. **Check Environment Variables:**
   - Dashboard → Your Service → "Environment" tab
   - Verify all variables are set correctly

3. **Test Locally First:**
   ```bash
   # Set environment variables
   export DATABASE_URL="your_local_db_url"
   export REDIS_URL="redis://localhost:6379/0"
   # ... set other variables
   
   # Run app
   uvicorn src:app --reload
   ```

4. **Common Commands:**
   ```bash
   # Generate JWT secret
   openssl rand -hex 32
   
   # Test database connection
   psql $DATABASE_URL
   
   # Test Redis connection
   redis-cli -u $REDIS_URL ping
   ```

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

---

## 🎉 Success!

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com/docs
```

**API Version:** v2  
**Endpoints:**
- `/api/v2/auth/*` - Authentication
- `/api/v2/orders/*` - Order management
- `/api/v2/review/*` - Reviews

---

**Need help?** Check the logs first, then review this guide step by step.
