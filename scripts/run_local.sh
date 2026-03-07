#!/usr/bin/env bash
# scripts/run_local.sh
# ─────────────────────────────────────────────────────────────────────────────
# Starts the Memora backend in a zero-config local demo mode.
#
# • Uses SQLite instead of PostgreSQL  – no database server required
# • Disables Celery workers            – no Redis required
# • Hot-reloads on code changes
#
# After startup visit: http://localhost:8000/docs
# ─────────────────────────────────────────────────────────────────────────────
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$REPO_ROOT/backend"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Memora – Local Demo Mode (SQLite)      ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# ── 1. Python venv ────────────────────────────────────────────────────────────
if [ ! -d "$BACKEND/venv" ]; then
  echo "  → Creating Python virtual environment…"
  python3 -m venv "$BACKEND/venv"
fi

source "$BACKEND/venv/bin/activate"

# ── 2. Install dependencies ───────────────────────────────────────────────────
echo "  → Installing / verifying Python dependencies…"
pip install -q --upgrade pip
pip install -q \
  fastapi uvicorn[standard] \
  sqlalchemy aiosqlite \
  "pydantic[email]" pydantic-settings \
  passlib[bcrypt] "python-jose[cryptography]" \
  python-multipart python-dotenv \
  dateparser python-dateutil

echo "  → Dependencies ready."
echo ""

# ── 3. Environment ────────────────────────────────────────────────────────────
export DATABASE_URL="sqlite+aiosqlite:///$BACKEND/memora_demo.db"
export SECRET_KEY="${SECRET_KEY:-local-demo-secret-key-change-before-deploying}"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
export ENVIRONMENT="development"
export LOG_LEVEL="WARNING"   # keep console clean; set INFO to see SQL
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"

# ── 4. Start server ───────────────────────────────────────────────────────────
echo "  ✅  Starting backend on http://localhost:8000"
echo "  📖  Interactive API docs: http://localhost:8000/docs"
echo "  📖  Alternative docs:     http://localhost:8000/redoc"
echo ""
echo "  Tip: Run 'python scripts/seed_demo.py' in a second terminal to seed"
echo "       the database with sample data."
echo ""
echo "  Press Ctrl+C to stop."
echo ""

cd "$BACKEND"
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level warning
