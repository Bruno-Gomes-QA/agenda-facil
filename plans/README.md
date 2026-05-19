# Plano — Agenda Fácil

Levantamento dividido em etapas. Cada `.md` é um pacote independente (Migration + API + FE) que pode ser entregue como MVP e validado por QA.

## Leia primeiro
- [00-overview.md](00-overview.md) — visão geral, papéis, mapa de rotas, fluxos.

## Infra
- [01-infra-docker.md](01-infra-docker.md) — Docker, Makefile (`make up-db`, `make up-api`).
- [02-schema-banco.md](02-schema-banco.md) — DDL de referência + seeds.

## Backend + Frontend por funcionalidade
- [03-auth-usuarios.md](03-auth-usuarios.md) — cadastro, login, papéis.
- [04-especialidades.md](04-especialidades.md) — CRUD de especialidades.
- [05-medicos.md](05-medicos.md) — cadastro de médicos (+ user de login).
- [06-disponibilidade.md](06-disponibilidade.md) — janelas semanais + slots.
- [07-agendamento-paciente.md](07-agendamento-paciente.md) — fluxo paciente.
- [08-agenda-recepcionista.md](08-agenda-recepcionista.md) — painel operador.
- [09-painel-medico.md](09-painel-medico.md) — agenda do médico.

## Frontend base
- [10-frontend-base.md](10-frontend-base.md) — Nuxt + bun + shadcn-vue + auth.

## QA
- [11-cenarios-qa.md](11-cenarios-qa.md) — catálogo de cenários de teste.

---

## Como usar este plano

1. **Você responde** as perguntas de refinamento (cada `.md` tem uma seção no final).
2. Confirmamos defaults ou ajustamos.
3. Executamos etapa por etapa, na ordem numérica.
4. Ao final de cada etapa, QA roda os cenários do módulo em [11-cenarios-qa.md](11-cenarios-qa.md).
