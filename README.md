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

## Quick Start

### With Docker (recommended)

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login, get tokens |
| GET | /api/memories | List memories with filters |
| POST | /api/memories/search | Semantic search |
| POST | /api/query | Natural language query |
| GET | /api/commitments | List commitments |
| GET | /api/tasks | List tasks |
| GET | /api/insights | Proactive insights |
| GET | /api/dashboard/summary | Daily summary |
| GET | /api/dashboard/weekly-review | Weekly review |
| POST | /api/privacy/export-data | Export all data |

Full interactive docs available at `/docs` when running.

## Environment Variables

See `.env.example` for all required variables. Key ones:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `SECRET_KEY` — JWT signing secret (change in production!)
- `OPENAI_API_KEY` — Optional, for GPT-4 answers + embeddings
- `ANTHROPIC_API_KEY` — Optional, for Claude answers

## Testing

```bash
cd backend
pytest tests/ -v
```

25 tests covering auth, memories, query, extraction pipeline, and retrieval engine.