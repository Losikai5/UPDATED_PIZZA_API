# Running Losika Pizza locally

The project has two parts:

- **Backend** — FastAPI API in `src/` (needs PostgreSQL + Redis)
- **Frontend** — React + Vite app in `Frontend/pizza/`

Run the backend first, then the frontend.

---

## 1. Backend (FastAPI)

### Prerequisites
- Python 3.11+
- PostgreSQL running locally
- Redis running locally (used for the auth token blocklist + Celery)

### Setup

```bash
# from the repo root
python -m venv venv
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### Configure environment

Copy the template and fill it in:

```bash
# Windows (PowerShell):
Copy-Item .env.example .env
# macOS/Linux:
# cp .env.example .env
```

Then edit `.env`:
- `DATABASE_URL` — point at your local Postgres DB, e.g.
  `postgresql+asyncpg://postgres:postgres@localhost:5432/mypizza_api`
  (create the database first: `createdb mypizza_api`)
- `REDIS_URL` — usually `redis://localhost:6379/0`
- `JWT_SECRET` — generate one: `openssl rand -hex 32`
- Mail settings — only needed for email verification / password reset.
  For local testing you can leave the Gmail values as placeholders; signup
  still creates the account (you just won't receive the verification email).

### Run database migrations

```bash
alembic upgrade head
```

### Start the API

```bash
uvicorn src:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

> The frontend expects the API at the base URL configured in
> `Frontend/pizza/src/services/api.js`. If your API runs somewhere other than
> the default, update that file.

---

## 2. Frontend (React + Vite)

### Prerequisites
- Node.js 18+

### Setup & run

```bash
cd Frontend/pizza
npm install
npm run dev
```

Open the printed URL (default **http://localhost:5173**).

The dev server proxies/calls the backend, so make sure the API from step 1 is
running before you try to log in or load the menu.

### Other commands

```bash
npm run build     # production build into dist/
npm run preview   # preview the production build
npm run lint      # eslint
```

---

## Quick start (both, two terminals)

```bash
# Terminal 1 — backend
venv\Scripts\Activate.ps1
uvicorn src:app --reload --port 8000

# Terminal 2 — frontend
cd Frontend/pizza
npm run dev
```

Then visit http://localhost:5173 and log in.
