#!/usr/bin/env bash
# =============================================================================
# scripts/setup-local.sh
# Setup ONE-TIME do ambiente local (sem Docker).
# Execute: bash scripts/setup-local.sh
# Requer sudo para instalar PostgreSQL.
# =============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}→ $*${NC}"; }
success() { echo -e "${GREEN}✓ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠ $*${NC}"; }
error()   { echo -e "${RED}✗ $*${NC}" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(dirname "$SCRIPT_DIR")"

cd "$API_DIR"
info "Diretório: $API_DIR"

# ── 1. PostgreSQL ─────────────────────────────────────────────────────────────
info "Verificando PostgreSQL..."
if command -v psql &>/dev/null; then
  success "PostgreSQL já instalado: $(psql --version)"
else
  info "Instalando PostgreSQL via apt..."
  sudo apt-get update -qq
  sudo apt-get install -y postgresql postgresql-contrib
  success "PostgreSQL instalado"
fi

# ── 2. Inicia o serviço PostgreSQL ────────────────────────────────────────────
info "Iniciando serviço PostgreSQL..."
sudo service postgresql start || sudo systemctl start postgresql 2>/dev/null || true

sleep 2

if ! pg_isready -q 2>/dev/null; then
  warn "pg_isready falhou — tentando direto..."
  sudo -u postgres pg_isready -q || error "PostgreSQL não iniciou. Verifique: sudo service postgresql status"
fi
success "PostgreSQL rodando"

# ── 3. Cria usuário e banco ───────────────────────────────────────────────────
info "Criando usuário 'agenda' e banco 'agenda_facil'..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename='agenda'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER agenda WITH PASSWORD 'agenda' CREATEDB;" 2>/dev/null || true

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='agenda_facil'" | grep -q 1 || \
  sudo -u postgres createdb -O agenda agenda_facil 2>/dev/null || \
  sudo -u postgres psql -c "CREATE DATABASE agenda_facil OWNER agenda;" 2>/dev/null || true

success "Banco de dados pronto"

# ── 4. Python venv ────────────────────────────────────────────────────────────
info "Configurando venv Python..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

.venv/bin/pip install --upgrade pip setuptools wheel --quiet
.venv/bin/pip install -e "." --quiet
success "Dependências Python instaladas"

# ── 5. Cria .env local se não existir ────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  success ".env criado a partir de .env.example"
else
  warn ".env já existe — mantendo"
fi

# ── 6. Migrations ─────────────────────────────────────────────────────────────
info "Rodando migrations Alembic..."
DATABASE_URL="postgresql+psycopg://agenda:agenda@localhost:5432/agenda_facil" \
  .venv/bin/alembic upgrade head
success "Migrations aplicadas"

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup concluído! Para iniciar a API:${NC}"
echo -e "${GREEN}  make run-api-local${NC}"
echo -e "${GREEN}  ou:${NC}"
echo -e "${GREEN}  cd api && bash scripts/run-api-local.sh${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
