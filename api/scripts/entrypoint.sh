#!/usr/bin/env sh
set -e

echo "→ Aguardando banco de dados..."
# Postgres já está healthy (healthcheck no compose), mas esperamos um segundo por segurança
sleep 1

echo "→ Rodando migrations Alembic..."
alembic upgrade head

echo "✓ Migrations aplicadas. Subindo API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
