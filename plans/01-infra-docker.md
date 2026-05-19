# Etapa 1 — Infraestrutura Docker + Makefile

> Subir Postgres limpo e API rodando migrations com um comando cada. Frontend roda fora do Docker (bun dev local) e enxerga a API via `localhost`.

---

## 1. Objetivo

- `make up-db` → sobe Postgres limpo (volume nomeado, fácil de resetar).
- `make up-api` → builda a imagem da API, sobe o container, **roda migrations Alembic automaticamente** no start e expõe `http://localhost:8000`.
- `make down`, `make reset-db`, `make logs`, `make psql`, `make migrate`, `make revision m="..."` como utilitários.
- FE roda com `bun dev` na máquina (WSL) → bate em `http://localhost:8000` pois a API publica a porta no host.

## 2. Decisões de rede

- Docker Compose cria uma rede interna `agenda_net`.
- Postgres: porta `5432` publicada no host como `5432` (para psql/DBeaver locais).
- API: porta `8000` publicada no host como `8000`.
- API dentro do container conecta no Postgres pelo nome do serviço: `db:5432`.
- FE (WSL local) conecta na API por `http://localhost:8000` — funciona porque no WSL2 o `localhost` é compartilhado com Windows e o container publica a porta.

## 3. Estrutura mínima nesta etapa

```
agenda-facil/
├── Makefile
├── docker-compose.yml
├── .env.example
├── api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py            # /health + registra routers (vazio nessa etapa)
│   │   └── core/
│   │       ├── config.py
│   │       └── database.py
│   └── scripts/
│       └── entrypoint.sh      # alembic upgrade head && uvicorn ...
└── front-end/                  # (Etapa 10 cuida da inicialização)
```

## 4. `docker-compose.yml` (esboço)

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: agenda_db
    environment:
      POSTGRES_USER: agenda
      POSTGRES_PASSWORD: agenda
      POSTGRES_DB: agenda_facil
    ports: ["5432:5432"]
    volumes:
      - agenda_pgdata:/var/lib/postgresql/data
    networks: [agenda_net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agenda -d agenda_facil"]
      interval: 3s
      retries: 10

  api:
    build: ./api
    container_name: agenda_api
    environment:
      DATABASE_URL: postgresql+psycopg://agenda:agenda@db:5432/agenda_facil
      SECRET_KEY: dev-secret-change-me
      CORS_ORIGINS: http://localhost:3000
    depends_on:
      db: { condition: service_healthy }
    ports: ["8000:8000"]
    networks: [agenda_net]
    command: ["/app/scripts/entrypoint.sh"]

volumes:
  agenda_pgdata:
networks:
  agenda_net:
```

## 5. `Makefile` (alvos previstos)

```makefile
.PHONY: up-db up-api down reset-db logs psql migrate revision fe-dev

up-db:
	docker compose up -d db

up-api:
	docker compose up -d --build api

down:
	docker compose down

reset-db:
	docker compose down -v
	docker compose up -d db

logs:
	docker compose logs -f api

psql:
	docker compose exec db psql -U agenda -d agenda_facil

migrate:
	docker compose exec api alembic upgrade head

revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

fe-dev:
	cd front-end && bun install && bun run dev
```

## 6. `entrypoint.sh` da API

```bash
#!/usr/bin/env sh
set -e
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 7. Endpoint `/health` (única rota dessa etapa)

`GET /health` → `{ "status": "ok", "db": "ok" }` (testa conexão SQL `SELECT 1`).

## 8. Critérios de aceite (QA)

- [ ] `make up-db` sobe Postgres e `make psql` conecta.
- [ ] `make reset-db` apaga volume e recria.
- [ ] `make up-api` builda, sobe, executa migrations (mesmo que vazias) e expõe `/health`.
- [ ] `curl http://localhost:8000/health` responde 200.
- [ ] Derrubar a API e subir de novo não duplica migrations.
- [ ] A partir do WSL, `bun dev` no FE consegue chamar `http://localhost:8000/health`.

## 9. Perguntas de refinamento

### P1. Postgres em volume nomeado ou bind mount?
**Default:** Volume nomeado (`agenda_pgdata`). É mais limpo e o `make reset-db` resolve com `down -v`.

### P2. Versão do Postgres?
**Default:** `postgres:16-alpine`.

### P3. API deve rodar com `--reload` no Docker?
**Default:** Sim, com bind mount de `./api/app` para `/app/app`, facilita o desenvolvimento. Em "modo limpo" o reload não atrapalha QA.

### P4. Frontend dentro do Docker também?
**Default:** **Não** — usuário pediu `bun dev` local. Mantemos FE fora do compose para velocidade de iteração.

### P5. Porta do FE?
**Default:** `3000` (padrão Nuxt). API libera CORS para `http://localhost:3000`.

### P6. Seeds rodam no entrypoint?
**Default:** Não nessa etapa. Etapa 2 define o mecanismo de seed (via migration de dados Alembic). Quando existir, rodará junto com `alembic upgrade head`.

### P7. Credenciais do Postgres?
**Default:** `agenda` / `agenda` em dev. Sem `.env` obrigatório — defaults no `docker-compose.yml`. `.env.example` documenta os overrides.

### P8. Precisamos de `make` para Windows puro?
**Default:** Não — projeto roda no WSL conforme contexto. Documentaremos no README mas não criaremos `.bat`.
