.PHONY: up-db up-api down reset-db logs psql migrate revision fe-dev help \
        setup-local run-api-local run-db-local

# ─── Banco de dados ────────────────────────────────────────────────────────────
up-db:
	@echo "→ Subindo Postgres..."
	docker compose up -d db
	@echo "✓ Postgres disponível em localhost:5432"

# ─── API ───────────────────────────────────────────────────────────────────────
up-api:
	@echo "→ Buildando e subindo API..."
	docker compose up -d --build api
	@echo "✓ API disponível em http://localhost:8000"
	@echo "✓ Docs em http://localhost:8000/docs"

# ─── Ambos ─────────────────────────────────────────────────────────────────────
up:
	docker compose up -d --build
	@echo "✓ Ambiente completo no ar"

# ─── Parar ─────────────────────────────────────────────────────────────────────
down:
	docker compose down

# ─── Reset completo do banco (apaga volume) ────────────────────────────────────
reset-db:
	@echo "⚠ Apagando volume do Postgres e recriando..."
	docker compose down -v
	docker compose up -d db
	@echo "✓ Banco limpo. Execute 'make up-api' para recriar tabelas e seeds."

# ─── Logs ──────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f api

logs-db:
	docker compose logs -f db

# ─── psql ──────────────────────────────────────────────────────────────────────
psql:
	docker compose exec db psql -U agenda -d agenda_facil

# ─── Alembic ───────────────────────────────────────────────────────────────────
migrate:
	docker compose exec api alembic upgrade head

rollback:
	docker compose exec api alembic downgrade -1

revision:
	@test -n "$(m)" || (echo "Uso: make revision m='descricao'" && exit 1)
	docker compose exec api alembic revision --autogenerate -m "$(m)"

# ─── Frontend ──────────────────────────────────────────────────────────────────
fe-dev:
	@echo "→ Instalando dependências e subindo frontend..."
	cd front-end && bun install && bun run dev

fe-install:
	cd front-end && bun install

# ─── Modo LOCAL (sem Docker) ───────────────────────────────────────────────────
# Use quando o Docker Desktop WSL integration não estiver habilitado.
# Requer: sudo para instalar Postgres na primeira execução.

setup-local:
	@echo "→ Setup local (instala Postgres + venv Python + migrations)..."
	bash api/scripts/setup-local.sh

run-db-local:
	@echo "→ Iniciando PostgreSQL local..."
	sudo service postgresql start 2>/dev/null || sudo systemctl start postgresql 2>/dev/null || true
	@echo "✓ Postgres local em localhost:5432"

run-api-local:
	@echo "→ Subindo API localmente (sem Docker)..."
	bash api/scripts/run-api-local.sh

# ─── Ajuda ─────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Agenda Fácil — Comandos disponíveis:"
	@echo ""
	@echo "  ── Com Docker Desktop (WSL integration habilitado) ──────────────"
	@echo "  make up-db        Sobe apenas o Postgres (porta 5432)"
	@echo "  make up-api       Builda e sobe a API (porta 8000) + roda migrations"
	@echo "  make up           Sobe banco + API juntos"
	@echo "  make down         Para todos os containers"
	@echo "  make reset-db     Apaga volume e recria banco zerado"
	@echo "  make logs         Acompanha logs da API em tempo real"
	@echo "  make psql         Abre shell psql no banco"
	@echo "  make migrate      Roda alembic upgrade head"
	@echo "  make rollback     Desfaz última migration"
	@echo "  make revision m=  Gera nova migration com autogenerate"
	@echo ""
	@echo "  ── Sem Docker (local via apt) ────────────────────────────────────"
	@echo "  make setup-local     Instala Postgres + venv + migrations (1x)"
	@echo "  make run-db-local    Inicia serviço PostgreSQL local"
	@echo "  make run-api-local   Roda API com uvicorn no venv local"
	@echo ""
	@echo "  ── Frontend ──────────────────────────────────────────────────────"
	@echo "  make fe-dev       Instala deps e sobe o frontend (bun dev)"
	@echo ""
