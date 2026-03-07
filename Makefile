# Memora – convenience targets
# ─────────────────────────────────────────────────────────────────────────────
# Requires: Docker + Docker Compose (for "docker" targets)
#           Python 3.11+ venv in backend/venv  (for "dev" targets)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help start stop restart logs shell-backend shell-db \
        backend-dev frontend-dev local-demo test demo-data build clean

# ── Default target ────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  Memora – Personal AI Memory System"
	@echo "  ==================================="
	@echo ""
	@echo "  DOCKER (recommended):"
	@echo "    make start        Start all services via Docker Compose"
	@echo "    make stop         Stop all services"
	@echo "    make restart      Rebuild images and restart services"
	@echo "    make logs         Tail logs for all services"
	@echo "    make logs s=X     Tail logs for a single service  (e.g. s=backend)"
	@echo "    make demo-data    Seed the running API with sample data"
	@echo ""
	@echo "  LOCAL DEVELOPMENT (no Docker):"
	@echo "    make local-demo   Start backend only, using SQLite (zero config)"
	@echo "    make backend-dev  Start backend dev server (needs .env + Postgres)"
	@echo "    make frontend-dev Start Next.js dev server"
	@echo ""
	@echo "  TESTING:"
	@echo "    make test         Run the full backend test suite"
	@echo ""
	@echo "  MISC:"
	@echo "    make build        Build Docker images without starting services"
	@echo "    make clean        Remove containers, volumes, and build artefacts"
	@echo "    make shell-backend  Open a shell inside the running backend container"
	@echo "    make shell-db       Open psql inside the running database container"
	@echo ""

# ── Docker targets ────────────────────────────────────────────────────────────

start:
	@[ -f .env ] || (cp .env.example .env && echo "Created .env from .env.example – edit it to add API keys.")
	docker compose up -d
	@echo ""
	@echo "  ✅  Memora is starting up!"
	@echo "  Frontend  → http://localhost:3000"
	@echo "  API       → http://localhost:8000"
	@echo "  API Docs  → http://localhost:8000/docs"
	@echo ""
	@echo "  Run 'make logs' to watch progress, or 'make demo-data' to seed sample data."

stop:
	docker compose down

restart:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

logs:
	docker compose logs -f $(s)

build:
	docker compose build

demo-data:
	@echo "Seeding the running API with demo data…"
	python3 scripts/seed_demo.py

shell-backend:
	docker compose exec backend bash

shell-db:
	docker compose exec db psql -U postgres -d memora

# ── Local development (no Docker) ────────────────────────────────────────────

local-demo:
	@echo "Starting Memora backend in local SQLite demo mode…"
	@echo "  No Docker, PostgreSQL, or Redis required."
	@echo ""
	bash scripts/run_local.sh

backend-dev:
	@[ -f backend/.env ] || (cp .env.example backend/.env && echo "Copied .env.example → backend/.env")
	cd backend && \
	  [ -d venv ] || python3 -m venv venv && \
	  . venv/bin/activate && \
	  pip install -q -r requirements.txt && \
	  alembic upgrade head && \
	  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm install && npm run dev

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	cd backend && \
	  [ -d venv ] || python3 -m venv venv && \
	  . venv/bin/activate && \
	  pip install -q -r requirements.txt 'pydantic[email]' && \
	  python -m pytest tests/ -v

# ── Clean-up ──────────────────────────────────────────────────────────────────

clean:
	docker compose down -v --remove-orphans
	rm -rf backend/venv backend/__pycache__ backend/*.db
	rm -rf frontend/node_modules frontend/.next
	@echo "Clean done."
