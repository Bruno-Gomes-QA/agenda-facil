# Etapa 2 — Schema do banco (referência) + Seeds

> DDL completo de referência. Cada etapa seguinte cria sua migration Alembic correspondente. Este arquivo é a **fonte da verdade do modelo de dados**.

---

## 1. Visão geral das tabelas

| Tabela | Etapa que cria | Resumo |
|---|---|---|
| `users` | 3 | Conta de acesso. Papel define o que pode fazer. |
| `patients` | 3 | Dados do paciente (1:1 com `users` quando papel = `paciente`) |
| `specialties` | 4 | Especialidades médicas |
| `doctors` | 5 | Médico (1:1 com `users` papel=`medico`, FK para `specialties`) |
| `doctor_availability_rules` | 6 | Janela semanal recorrente (dia da semana + hora início/fim) |
| `appointments` | 7 | Consulta agendada |
| `appointment_history` | 7 | (opcional) log de mudanças de status |

## 2. SQL base de referência

```sql
-- =========================
-- USERS / AUTH (Etapa 3)
-- =========================
CREATE TYPE user_role AS ENUM ('paciente', 'recepcionista', 'medico');

CREATE TABLE users (
  id           BIGSERIAL PRIMARY KEY,
  name         VARCHAR(120)  NOT NULL,
  email        VARCHAR(160)  NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role         user_role     NOT NULL,
  phone        VARCHAR(20),
  is_active    BOOLEAN       NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_role ON users(role);

-- Dados extras do paciente (opcional, mantém users enxuto)
CREATE TABLE patients (
  user_id     BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  cpf         VARCHAR(14) UNIQUE,
  birth_date  DATE
);

-- =========================
-- ESPECIALIDADES (Etapa 4)
-- =========================
CREATE TABLE specialties (
  id          BIGSERIAL PRIMARY KEY,
  name        VARCHAR(120) NOT NULL UNIQUE,
  description TEXT,
  is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- MÉDICOS (Etapa 5)
-- =========================
CREATE TABLE doctors (
  id            BIGSERIAL PRIMARY KEY,
  user_id       BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE RESTRICT,
  specialty_id  BIGINT NOT NULL REFERENCES specialties(id) ON DELETE RESTRICT,
  crm           VARCHAR(20) NOT NULL UNIQUE,
  bio           TEXT,
  is_active     BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_doctors_specialty ON doctors(specialty_id);

-- =========================
-- DISPONIBILIDADE (Etapa 6)
-- Janelas recorrentes por dia da semana
-- =========================
-- weekday: 0=domingo ... 6=sábado (padrão ISO ou Python? Padronizar Python: 0=segunda ... 6=domingo)
CREATE TABLE doctor_availability_rules (
  id          BIGSERIAL PRIMARY KEY,
  doctor_id   BIGINT NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
  weekday     SMALLINT NOT NULL CHECK (weekday BETWEEN 0 AND 6),
  start_time  TIME NOT NULL,
  end_time    TIME NOT NULL,
  CHECK (end_time > start_time)
);
CREATE INDEX idx_avail_doctor ON doctor_availability_rules(doctor_id);

-- =========================
-- CONSULTAS (Etapa 7)
-- =========================
CREATE TYPE appointment_status AS ENUM ('agendada', 'cancelada', 'realizada', 'no_show');

CREATE TABLE appointments (
  id              BIGSERIAL PRIMARY KEY,
  patient_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  doctor_id       BIGINT NOT NULL REFERENCES doctors(id) ON DELETE RESTRICT,
  scheduled_at    TIMESTAMPTZ NOT NULL,                   -- início da consulta
  duration_min    SMALLINT    NOT NULL DEFAULT 30,
  status          appointment_status NOT NULL DEFAULT 'agendada',
  reason          VARCHAR(255),                            -- motivo informado pelo paciente
  doctor_notes    TEXT,                                    -- nota clínica (médico)
  created_by      BIGINT REFERENCES users(id),             -- quem criou (paciente ou recepcionista)
  rescheduled_at  TIMESTAMPTZ,                             -- última remarcação
  cancelled_at    TIMESTAMPTZ,
  cancelled_by    BIGINT REFERENCES users(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Impede dois agendamentos com mesmo médico no mesmo horário (status agendada)
CREATE UNIQUE INDEX uniq_doctor_slot_active
  ON appointments(doctor_id, scheduled_at)
  WHERE status = 'agendada';

CREATE INDEX idx_appt_patient ON appointments(patient_id);
CREATE INDEX idx_appt_doctor_date ON appointments(doctor_id, scheduled_at);
CREATE INDEX idx_appt_status ON appointments(status);

-- Histórico de mudanças (opcional, gera mais cenários de QA)
CREATE TABLE appointment_history (
  id              BIGSERIAL PRIMARY KEY,
  appointment_id  BIGINT NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
  changed_by      BIGINT REFERENCES users(id),
  from_status     appointment_status,
  to_status       appointment_status,
  note            VARCHAR(255),
  changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 3. Seeds iniciais

Migration de dados (Alembic) `0002_seed_initial.py`:

- 1 recepcionista: `admin@agendafacil.local` / `admin123`
- Especialidades: `Clínico Geral`, `Cardiologia`, `Dermatologia`, `Pediatria`, `Ortopedia`
- 2 médicos demo:
  - `dr.house@agendafacil.local` / `house123` — Clínico Geral, CRM `12345-SP`
  - `dra.grey@agendafacil.local` / `grey123` — Cardiologia, CRM `67890-SP`
  - Cada um com janela `seg-sex 08:00–12:00 e 14:00–18:00`
- 1 paciente demo: `paciente@agendafacil.local` / `paciente123`

## 4. Convenções

- Todos os timestamps em `TIMESTAMPTZ` (UTC no banco; FE converte para `America/Sao_Paulo`).
- IDs `BIGSERIAL`.
- `is_active` para soft-disable em vez de `DELETE` em `specialties`, `doctors`, `users`.
- `DELETE` físico permitido apenas em `appointments` via cancelamento lógico (`status='cancelada'`).

## 5. Critérios de aceite (QA)

- [ ] Após `make up-api`, todas as tabelas existem.
- [ ] Seeds criaram usuários demo e especialidades.
- [ ] `SELECT COUNT(*) FROM doctors;` retorna 2.
- [ ] Index único impede inserir duas consultas no mesmo `(doctor_id, scheduled_at)` com status `agendada`.

## 6. Perguntas de refinamento

### P1. Usar ENUM nativo do Postgres ou VARCHAR + CHECK?
**Default:** ENUM nativo (`user_role`, `appointment_status`). Mais limpo; Alembic+SQLAlchemy lidam bem.

### P2. Separar paciente em tabela `patients` ou deixar tudo em `users`?
**Default:** Tabela `patients` separada com FK 1:1. Mantém `users` enxuto e só com dados de auth. Médicos/recepcionistas não precisam de `birth_date`/`cpf`.

### P3. Médico tem `user_id` obrigatório?
**Default:** Sim — todo médico no sistema tem login (mesmo que use pouco). Simplifica RBAC.

### P4. Duração da consulta é fixa ou por médico?
**Default:** Fixa em 30min no MVP (`duration_min DEFAULT 30`). Coluna existe para evoluir depois.

### P5. Soft delete em médicos/especialidades?
**Default:** Sim, via `is_active`. Excluir fisicamente médico com consultas históricas quebraria o histórico.

### P6. Histórico (`appointment_history`) entra no MVP?
**Default:** Sim — é barato e gera muitos cenários de teste interessantes (auditoria, "quem cancelou", etc.).

### P7. Timezone no banco?
**Default:** `TIMESTAMPTZ` armazenando UTC. API recebe/devolve em ISO 8601 com timezone. FE exibe em `America/Sao_Paulo`.

### P8. Constraint para "uma consulta por médico por horário": índice parcial ou check completo?
**Default:** Índice único parcial em `(doctor_id, scheduled_at) WHERE status='agendada'`. Permite múltiplas canceladas no mesmo slot (caso real).

### P9. Paciente pode ter múltiplas consultas no mesmo horário (médicos diferentes)?
**Default:** Banco permite, **service bloqueia** com 409. Mais flexível para evoluir.

### P10. Convenção de weekday?
**Default:** `0=segunda ... 6=domingo` (padrão Python `weekday()`). Documentar no schema.
