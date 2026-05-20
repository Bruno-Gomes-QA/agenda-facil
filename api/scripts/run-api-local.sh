#!/usr/bin/env bash
# =============================================================================
# scripts/run-api-local.sh
# Inicia a API FastAPI localmente (sem Docker).
# Requer: setup-local.sh já executado.
# Execute: bash scripts/run-api-local.sh
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(dirname "$SCRIPT_DIR")"
cd "$API_DIR"

# Garante que postgres está rodando
if ! pg_isready -h localhost -p 5432 -U agenda -d agenda_facil -q 2>/dev/null; then
  echo "→ Iniciando PostgreSQL..."
  sudo service postgresql start 2>/dev/null || sudo systemctl start postgresql 2>/dev/null || true
  sleep 2
fi

# Carrega .env local
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs 2>/dev/null) || true
fi

# Usa banco local por padrão se DATABASE_URL não estiver setada
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://agenda:agenda@localhost:5432/agenda_facil}"

echo "→ Rodando migrations..."
.venv/bin/alembic upgrade head

echo "✓ Iniciando API em http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
