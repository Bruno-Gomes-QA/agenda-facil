# Status de Implementação — Agenda Fácil

> Atualizar este arquivo a cada etapa concluída. Agentes e sessões futuras devem consultá-lo para saber o que está implementado.

---

## Resumo

| Etapa | Status | Data | Arquivos principais |
|---|---|---|---|
| **01 — Infra Docker** | ✅ Implementado | 2026-05-19 | `docker-compose.yml`, `Makefile`, `api/Dockerfile`, `api/scripts/entrypoint.sh` |
| **02 — Schema banco** | ✅ Implementado | 2026-05-19 | `api/alembic/versions/0001_create_users.py`, `api/alembic/versions/0002_seed_initial_data.py` |
| **03 — Auth/Usuários** | ✅ Implementado | 2026-05-19 | `api/app/modules/users/` (models, schemas, service, router), `api/app/core/deps.py` |
| **04 — Especialidades** | ✅ Implementado | 2026-05-20 | `api/app/modules/specialties/` + `0003_create_specialties.py`; FE `pages/admin/specialties/index.vue`, `composables/api/specialties/useSpecialties.ts` |
| **05 — Médicos** | ✅ Implementado | 2026-05-20 | `api/app/modules/doctors/` + `0004_create_doctors.py`; FE `pages/doctors/`, `pages/admin/doctors/`, `composables/api/doctors/useDoctors.ts` |
| **06 — Disponibilidade** | ✅ Implementado | 2026-05-20 | `api/app/modules/availability/` + `0005_create_availability.py`; FE `pages/admin/doctors/[id].vue`, `pages/doctor/availability.vue`, `composables/api/availability/useAvailability.ts` |
| **07 — Agendamento (paciente)** | ✅ Implementado | 2026-05-20 | `api/app/modules/appointments/` + `0006_create_appointments.py`; FE `pages/appointments/*`, `composables/api/appointments/useAppointments.ts` |
| **08 — Painel recepcionista** | ✅ Implementado | 2026-05-20 | `api/app/modules/admin/`, endpoints admin em `appointments/router.py`; FE `pages/admin/*` (dashboard, pacientes, agendamentos, agenda) |
| **09 — Painel médico** | ✅ Implementado | 2026-05-20 | Endpoints `/doctors/me`, `/appointments/doctor/*`; FE `pages/doctor/agenda.vue`, `pages/doctor/appointments/[id].vue`, `pages/doctor/patients/index.vue` |
| **10 — Frontend base** | ✅ Implementado | 2026-05-19 | `front-end/` (Nuxt 4, Tailwind, login, register, auth store) |
| **11 — Cenários QA** | ⬜ Pendente | — | Smoke-test manual após `make up-api` |

---

## Como subir o ambiente

```bash
# 1. Banco de dados
make up-db

# 2. API (builda, migra, sobe)
make up-api

# 3. Frontend (WSL local, fora do Docker)
make fe-dev
# ou manualmente:
cd front-end && bun install && bun run dev
```

Frontend em `http://localhost:3000` → API em `http://localhost:8000`.

---

## Credenciais de teste (seeds)

| Email | Senha | Papel |
|---|---|---|
| admin@agendafacil.local | admin123 | recepcionista |
| dr.house@agendafacil.local | house123 | medico |
| dra.grey@agendafacil.local | grey123 | medico |
| paciente@agendafacil.local | paciente123 | paciente |

---

## Estado do banco (tabelas existentes)

Tabelas criadas pelas migrations 0001–0006:

- `users` — todos os papéis (paciente, recepcionista, medico)
- `patients` — dados extras do paciente (1:1 com users)
- `specialties` — catálogo de especialidades
- `doctors` — perfil profissional (1:1 com users de role=medico)
- `doctor_availability_rules` — janelas semanais (RRULE-like) por médico
- `appointments` + `appointment_history` — consultas e auditoria de mudança de status

---

## API endpoints disponíveis

### Públicos
- `GET /health` — status da API e banco
- `POST /users` — cadastro de paciente
- `POST /auth/login` — login (todos os papéis)

### Autenticados (qualquer papel)
- `GET /auth/me` — perfil do usuário logado
- `POST /auth/logout` — logout (stateless, client descarta token)
- `GET /users/{id}` — detalhe do usuário (próprio ou recepcionista)

### Recepcionista only
- `POST /users/staff` — criar recepcionista ou médico
- `POST /admin/patients`, `GET /admin/patients` — gestão de pacientes
- `POST /specialties`, `PUT /specialties/{id}`, `DELETE /specialties/{id}` — gestão de especialidades
- `POST /doctors`, `PUT /doctors/admin/{id}`, `DELETE /doctors/admin/{id}` — gestão de médicos
- `POST /doctors/{id}/availability`, `DELETE /availability/{id}` — gestão de disponibilidade (também acessível ao próprio médico)
- `POST /appointments/admin`, `GET /appointments/admin`, `PATCH /appointments/admin/{id}/status` — gestão de agendamentos

### Médico
- `GET /doctors/me` — perfil do médico logado
- `GET /appointments/doctor` — agenda do médico logado
- `PATCH /appointments/doctor/{id}/status` — atualizar status (atendido/cancelado/no_show)
- `POST /doctors/me/availability`, `DELETE /availability/{id}` — gerenciar própria agenda

### Paciente
- `GET /specialties`, `GET /doctors`, `GET /doctors/{id}` — descoberta pública
- `GET /doctors/{id}/availability/slots?from=&to=` — slots livres
- `POST /appointments`, `GET /appointments`, `GET /appointments/{id}`, `PATCH /appointments/{id}/cancel` — fluxo do paciente

---

## Frontend (Nuxt 4 SPA)

Páginas implementadas:

- **Públicas:** `/`, `/login`, `/register`, `/doctors`, `/doctors/:id`
- **Paciente:** `/appointments`, `/appointments/new`, `/appointments/:id`
- **Recepcionista:** `/admin` (dashboard), `/admin/specialties`, `/admin/doctors`, `/admin/doctors/:id`, `/admin/patients`, `/admin/appointments`, `/admin/appointments/new`, `/admin/agenda`
- **Médico:** `/doctor/agenda`, `/doctor/availability`, `/doctor/appointments/:id`, `/doctor/patients`

Composables (`app/composables/`):

- `core/useApi.ts` — wrapper de `$fetch` com Bearer + tratamento 401 + `apiErrorMessage`
- `api/{specialties,doctors,availability,appointments}/use*.ts` + `api/admin/{useAdminPatients,useStaff}.ts`

Guard de rota: `middleware/auth.ts` (`requiredRoles` via `definePageMeta`).

---

## Notas para o próximo agente/sessão

- **Etapas 1–10 ✅ implementadas.** Falta apenas etapa 11 (validação manual com QA scripts em `plans/11-cenarios-qa.md`).
- Backend FastAPI carrega sem erros (`from app.main import app`).
- Frontend Nuxt 4 builda com sucesso em **Node 24+** (`node ./node_modules/nuxt/bin/nuxt.mjs build`). Bun/Node 20 falham por incompatibilidade do `oxc-parser` (requer `require()` de ESM, disponível só a partir do Node 22).
- Para subir o ambiente completo: `make up-api` (aplica migrations 0001–0006 com seeds) e `make fe-dev` (com `nvm use 24`).
- Ao criar novos models, importar no `api/alembic/env.py` (linha `# ADD IMPORTS HERE`).
- FE usa `ssr: false` (SPA mode). Token JWT em memória + `sessionStorage`.
- CORS configurado para `http://localhost:3000`.
