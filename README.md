# Memora - Personal AI Memory System

> A production-oriented personal memory intelligence system that unifies fragmented user data into a persistent, privacy-aware, structured memory graph for retrieval, reasoning, and proactive task support.

## Product Vision

Memora acts as a user's persistent, private, intelligent memory layer across their digital life:
- *"What promises did I make last week?"*
- *"What unresolved tasks have I ignored for 10+ days?"*
- *"Summarize all my thinking about startup ideas over the last 3 months."*

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 + pgvector extension |
| Cache / Queue | Redis 7, Celery |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) or OpenAI |
| LLM | OpenAI GPT-4o-mini / Anthropic Claude (configurable) |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Auth | JWT (access + refresh tokens), bcrypt |
| Infrastructure | Docker Compose |

## Architecture

```
User Input / Connected Sources
        │
        ▼
┌─────────────────┐
│  Connectors      │  Gmail · Calendar · Notion · Notes · Meeting
└────────┬────────┘
         │ SourceDocument
         ▼
┌─────────────────┐
│  Extraction      │  Entity · Commitment · Task · Date · Topic · Salience
│  Pipeline        │
└────────┬────────┘
         │ Memories + Entities
         ▼
┌─────────────────┐
│  Storage         │  PostgreSQL (structured) + pgvector (embeddings)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
Retrieval   Proactive
Engine      Engine
    │         │
    └────┬────┘
         ▼
  Reasoning Engine  →  Grounded Answer + Citations
```

## Features

- **Smart Capture**: Ingest emails, calendar events, Notion pages, meeting transcripts, and notes
- **Memory Extraction**: Multi-stage pipeline extracts facts, commitments, tasks, events, goals
- **Hybrid Retrieval**: Combines semantic vector search (pgvector) + keyword search + metadata filters
- **Grounded Answers**: LLM-generated answers with source citations and confidence scores
- **Proactive Intelligence**: Detects overdue commitments, stale tasks, schedule conflicts, weekly summaries
- **Privacy First**: Per-user data isolation, soft deletes, full data export, audit trail

## Project Structure

```
├── backend/          # Python FastAPI application
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── connectors/   # Data source connectors
│   │   ├── extraction/   # Memory extraction pipeline
│   │   ├── retrieval/    # Hybrid retrieval engine
│   │   ├── reasoning/    # Answer generation
│   │   ├── consolidation/# Dedup & linking
│   │   ├── proactive/    # Insight generation
│   │   ├── services/     # Business logic
│   │   ├── workers/      # Celery background tasks
│   │   └── utils/        # Embeddings, LLM, text utils
│   ├── alembic/      # Database migrations
│   └── tests/        # pytest test suite (25 passing)
├── frontend/         # Next.js 15 TypeScript application
│   └── src/
│       ├── app/      # App Router pages
│       ├── components/
│       ├── hooks/
│       ├── lib/
│       └── types/
├── docker-compose.yml
└── .env.example
```

## Running the Project

Choose the approach that fits your setup:

| Approach | Requirements | Best for |
|---|---|---|
| [Option A – Docker Compose](#option-a--docker-compose-recommended) | Docker Desktop | Full production-like stack |
| [Option B – Local demo (SQLite)](#option-b--local-demo-no-docker) | Python 3.11+ only | Quick exploration, no setup |
| [Option C – Manual setup](#option-c--manual-setup) | Python + Node + PostgreSQL + Redis | Active development |

---

### Option A – Docker Compose (recommended)

**Prerequisites:** [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)

```bash
# 1. Clone (if you haven't already)
git clone https://github.com/Yashu-16/Personal-AI-Memory-System.git
cd Personal-AI-Memory-System

# 2. Copy the environment template
cp .env.example .env
#    Optional: open .env and add an OPENAI_API_KEY or ANTHROPIC_API_KEY
#    for full LLM-powered answers.  Everything works without one.

# 3. Start all services (first run downloads images and builds – ~3 min)
make start
#  or: docker compose up -d
```

Once all containers are healthy you will see:

```
  ✅  Memora is starting up!
  Frontend  → http://localhost:3000
  API       → http://localhost:8000
  API Docs  → http://localhost:8000/docs
```

```bash
# 4. Watch the startup logs
make logs
# press Ctrl+C when you see "Application startup complete" in the backend logs

# 5. Seed the database with rich sample data
make demo-data
#  or: python scripts/seed_demo.py
```

The seed script registers a demo account and creates 8 sample memories
(meetings, notes, commitments, ideas). At the end it prints:

```
  Demo user credentials:
    Email:    demo@example.com
    Password: Demo1234!

  Explore the system:
    API Docs  → http://localhost:8000/docs
    Frontend  → http://localhost:3000
```

**Stop everything:**
```bash
make stop
```

---

### Option B – Local demo (no Docker)

Runs the backend only, using SQLite.  No database server or Redis needed.

**Prerequisites:** Python 3.11+

```bash
# 1. Start the backend (creates a venv, installs deps, starts uvicorn)
make local-demo
#  or: bash scripts/run_local.sh
```

Output:
```
  ✅  Starting backend on http://localhost:8000
  📖  Interactive API docs: http://localhost:8000/docs
```

```bash
# 2. In a second terminal – seed sample data
pip install httpx          # only needed once
python scripts/seed_demo.py
```

Then open **http://localhost:8000/docs** in your browser.

> **Note:** The frontend requires Node.js and a running PostgreSQL database.
> For a frontend + full-stack experience use Option A.

---

### Option C – Manual setup

**Prerequisites:** Python 3.11+, Node.js 20+, PostgreSQL 16 (with pgvector), Redis 7

**Backend:**
```bash
cd backend

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env: set DATABASE_URL and REDIS_URL to your local services

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (separate terminal):
```bash
cd frontend
npm install
npm run dev
```

---

## What you'll see

### Interactive API Docs (`/docs`)

Swagger UI at **http://localhost:8000/docs** lets you call every endpoint
directly from your browser without any extra tooling.

**Quick demo flow via the docs UI:**

1. **Register** – `POST /api/auth/register`
   ```json
   { "email": "you@example.com", "password": "Secret123!", "full_name": "Your Name" }
   ```

2. **Login** – `POST /api/auth/login`  → copy the `access_token`

3. Click **Authorize** (🔒 top-right), paste `Bearer <your_token>`

4. **Add a memory** – `POST /api/memories`
   ```json
   {
     "content": "I promised Alice I would send the contract by Friday.",
     "source_type": "note"
   }
   ```

5. **Ask a natural-language question** – `POST /api/query`
   ```json
   { "query": "What commitments do I have this week?" }
   ```
   Response includes an `answer`, a `confidence` score, and `source_memories`
   citations.

6. **Browse your memories** – `GET /api/memories`

7. **Get a dashboard summary** – `GET /api/dashboard/summary`

### Frontend (`http://localhost:3000`)

| Page | URL | What it shows |
|---|---|---|
| Dashboard | `/` | Daily summary, stats, memory timeline |
| Chat | `/chat` | Natural-language query interface |
| Memories | `/memories` | Filterable memory browser |
| Tasks | `/tasks` | Extracted tasks with status |
| Commitments | `/commitments` | Promises and deadlines |
| Insights | `/insights` | Proactive AI insights |
| Weekly Review | `/weekly-review` | AI-generated weekly summary |
| Settings | `/settings` | Export / delete your data |

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login, get tokens |
| POST | /api/auth/refresh | Refresh access token |
| GET | /api/memories | List memories with filters |
| POST | /api/memories | Create a memory |
| POST | /api/memories/search | Semantic search |
| DELETE | /api/memories/{id} | Delete a memory |
| POST | /api/query | Natural language query |
| GET | /api/commitments | List commitments |
| GET | /api/tasks | List tasks |
| GET | /api/insights | Proactive insights |
| GET | /api/dashboard/summary | Daily summary |
| GET | /api/dashboard/weekly-review | Weekly review |
| GET | /api/sources | Connected data sources |
| POST | /api/privacy/export-data | Export all user data |
| DELETE | /api/privacy/delete-account | Delete account & data |

Full interactive docs at **http://localhost:8000/docs** when running.

---

## Environment Variables

See `.env.example` for all variables. Most have safe defaults for development.

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL async URL |
| `REDIS_URL` | ✅ | — | Redis URL |
| `SECRET_KEY` | ✅ | dev default | Change before deploying |
| `OPENAI_API_KEY` | ➖ | (empty) | Enables GPT-4o answers & embeddings |
| `ANTHROPIC_API_KEY` | ➖ | (empty) | Enables Claude answers |
| `GOOGLE_CLIENT_ID` | ➖ | (empty) | Gmail / Calendar connector |
| `NOTION_API_KEY` | ➖ | (empty) | Notion connector |

> Without an LLM key the query endpoint returns keyword-matched answers
> rather than AI-generated ones.  All other features work fully.

---

## Makefile reference

```
make start        Start all services (Docker)
make stop         Stop all services
make restart      Rebuild + restart
make logs         Stream all logs  (make logs s=backend for one service)
make demo-data    Seed the running API with sample data
make local-demo   Start backend only in SQLite mode (no Docker)
make backend-dev  Start backend dev server (needs .env + Postgres)
make frontend-dev Start Next.js dev server
make test         Run the backend test suite
make build        Build Docker images without starting
make clean        Remove containers, volumes, build artefacts
make shell-backend  Shell into the running backend container
make shell-db       psql into the running database container
```

## Testing

```bash
make test
# or manually:
cd backend && python -m pytest tests/ -v
```

25 tests covering auth, memories, query, extraction pipeline, and retrieval engine.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `docker compose up` hangs | Run `make logs` – usually Postgres is still initialising. Wait ~30 s. |
| `Connection refused` on port 8000 | Check `make logs s=backend` for Python import errors |
| `pydantic[email]` error | `pip install 'pydantic[email]'` in your venv |
| Frontend shows blank page | Ensure `NEXT_PUBLIC_API_URL` in `.env` points to the correct backend |
| `pgvector extension not found` | Use the `pgvector/pgvector:pg16` image (already in docker-compose.yml) |
| Port already in use | `make stop` then `make start`, or change ports in `docker-compose.yml` |