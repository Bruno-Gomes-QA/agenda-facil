# Plano Geral — Agenda Fácil

> Documento mestre. Cada etapa subsequente (`01..N`) entrega um MVP funcional por funcionalidade (Migration + API + FE) e pode ser testado isoladamente pelo time de QA.

---

## 1. Objetivo

Subir o sistema **Agenda Fácil** completo localmente (Postgres + API FastAPI + Frontend Nuxt 4) com foco em **gerar muitos cenários de teste** para a disciplina de QA. Segurança e performance são secundárias — robustez funcional é prioridade.

## 2. Stack consolidada

| Camada | Tecnologia |
|---|---|
| Banco | PostgreSQL 16 (Docker) |
| API | Python 3.11 + FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2 |
| Frontend | Nuxt 4 + Vue 3 + TypeScript + Tailwind 3 + shadcn-vue |
| Orquestração | Docker Compose + Makefile |
| Package manager FE | **bun** (obrigatório) |

## 3. Atores e papéis

| Papel | Como obtém acesso | O que pode fazer |
|---|---|---|
| **Visitante** | Sem login | Ver home, ver lista pública de médicos/especialidades, cadastrar-se como paciente, fazer login |
| **Paciente** | Auto-cadastro (rota pública) | Buscar médicos, consultar disponibilidade, agendar/remarcar/cancelar suas próprias consultas, ver histórico |
| **Recepcionista** | Criado por outro recepcionista (ou seed inicial) | Tudo de paciente + agendar em nome de pacientes, gerenciar cadastros de médicos/especialidades, cancelar/remarcar qualquer consulta, ver agenda de qualquer médico |
| **Médico** | Criado por recepcionista (login enviado por fora) | Ver sua própria agenda, marcar consulta como `realizada`/`no_show`, adicionar notas clínicas, ver dados do paciente da consulta |

## 4. Mapa de funcionalidades (ordem de entrega = MVPs)

| Etapa | Arquivo | Entrega | Testável ao fim |
|---|---|---|---|
| 1 | `01-infra-docker.md` | Compose + Makefile (`make up-db`, `make up-api`), API "hello world", migrations rodando | `curl /health` retorna 200; psql conecta no banco |
| 2 | `02-schema-banco.md` | Schema SQL base (DDL de referência) e seeds | Tabelas existem; seed cria recepcionista admin e especialidades |
| 3 | `03-auth-usuarios.md` | Cadastro paciente + login (todos os papéis) + `/me` + middleware FE | Login funciona para 3 papéis; rota protegida bloqueia sem token |
| 4 | `04-especialidades.md` | CRUD de especialidades (recepcionista) + listagem pública | Listar/criar/editar/deletar especialidades |
| 5 | `05-medicos.md` | CRUD de médicos + criação de credencial de login do médico | Recepcionista cadastra médico; médico consegue logar |
| 6 | `06-disponibilidade.md` | Janelas de atendimento do médico (dias da semana + intervalo) + cálculo de slots livres | GET `/doctors/{id}/availability?date=` retorna slots respeitando agendamentos |
| 7 | `07-agendamento-paciente.md` | Paciente agenda/remarca/cancela própria consulta + tela de "minhas consultas" | Fluxo completo do paciente |
| 8 | `08-agenda-recepcionista.md` | Recepcionista agenda em nome de paciente + visão de agenda diária por médico | Recepcionista gerencia consultas de terceiros |
| 9 | `09-painel-medico.md` | Médico vê sua agenda do dia, marca consulta como realizada/no_show, anota observação | Fluxo do médico |
| 10 | `10-frontend-base.md` | Setup Nuxt + Tailwind + shadcn-vue + `useApiFetch` + store de auth + layouts | Base FE rodando contra API real |
| 11 | `11-cenarios-qa.md` | Catálogo de cenários de teste manual/automatizado por funcionalidade | Lista pronta para Camila/Vitor executarem |

> **Nota:** A etapa 10 (frontend base) tecnicamente precede as etapas 3+ no FE, mas listo depois porque cada etapa funcional já descreve suas telas; a base é um pacote único de setup.

## 5. Fluxos principais (visão de produto)

### 5.1 Paciente novo agenda primeira consulta
1. Entra na home → vê CTA "Agendar consulta".
2. Clica → vai para `/register` (auto-cadastro paciente, rota pública).
3. Após cadastro, é autologado e redirecionado para `/doctors`.
4. Filtra por especialidade → escolhe médico → vê calendário → escolhe slot → confirma.
5. Vê consulta listada em `/appointments`.

### 5.2 Recepcionista agenda para paciente por telefone
1. Login em `/login` como recepcionista.
2. Vai em `/admin/appointments/new`.
3. Busca paciente por email/CPF ou cadastra novo paciente rápido.
4. Escolhe médico + slot + observação.
5. Confirma → consulta criada com status `agendada`.

### 5.3 Médico no consultório
1. Login → vai direto para `/doctor/agenda` (agenda do dia).
2. Vê lista de pacientes do dia com horário.
3. Clica em consulta → marca como `realizada` ou `no_show` + adiciona nota.

## 6. Rotas (resumo)

### Públicas (sem auth)
- `GET /health`
- `POST /users` (auto-cadastro paciente)
- `POST /auth/login`
- `GET /specialties`
- `GET /doctors` (listagem pública resumida — nome, especialidade, CRM)
- `GET /doctors/{id}` (detalhe público)

### Autenticadas (qualquer papel logado)
- `GET /auth/me`
- `POST /auth/logout`
- `GET /doctors/{id}/availability?date=YYYY-MM-DD`

### Paciente
- `GET /appointments/me`
- `POST /appointments` (cria para si)
- `PATCH /appointments/{id}` (remarca — só se for dele)
- `DELETE /appointments/{id}` (cancela — só se for dele)

### Recepcionista
- `POST /specialties`, `PATCH /specialties/{id}`, `DELETE /specialties/{id}`
- `POST /doctors`, `PATCH /doctors/{id}`, `DELETE /doctors/{id}`
- `POST /doctors/{id}/availability-rules` (janelas semanais)
- `GET /appointments` (lista geral com filtros)
- `POST /appointments` (em nome de paciente, exige `patient_id`)
- `PATCH/DELETE /appointments/{id}` (qualquer consulta)
- `POST /users/staff` (criar recepcionista ou médico — credencial)

### Médico
- `GET /appointments/doctor/me`
- `PATCH /appointments/{id}/status` (`realizada` | `no_show`)
- `PATCH /appointments/{id}/notes`

## 7. Convenção de status de consulta

```
agendada → realizada
agendada → cancelada
agendada → no_show
agendada → remarcada (na prática: cancela + cria nova)
```

Para simplificar testes, usamos **transições estritas** (apenas `agendada` pode mudar de status; consultas já finalizadas são imutáveis).

## 8. Como cada etapa é entregue

Cada `.md` numerado contém:
1. **Objetivo** da etapa.
2. **Migration** (DDL/Alembic) necessária.
3. **API** — endpoints, schemas Pydantic, regras de service.
4. **FE** — telas, componentes, composables.
5. **Critérios de aceite** (o que QA vai validar).
6. **Perguntas de refinamento** (com resposta default).

## 9. Perguntas de refinamento gerais

### P1. Confirmar os 3 papéis (paciente / recepcionista / médico)?
**Default:** Sim, exatamente esses 3. "Médico" e "recepcionista" são `staff` e são criados por outro recepcionista. Paciente é auto-cadastro público.

### P2. Listagem de médicos é pública (sem login)?
**Default:** Sim — paciente precisa "ver o catálogo" antes de criar conta. Disponibilidade e agendamento exigem login.

### P3. Paciente pode se cadastrar sozinho?
**Default:** Sim, rota pública `POST /users` cria apenas papel `paciente`. Criar recepcionista/médico exige outro recepcionista autenticado.

### P4. Recepcionista inicial: como é criado?
**Default:** Via **seed do Alembic** na primeira migration de dados (`email: admin@agendafacil.local`, `senha: admin123`). Em ambiente de testes isso é aceitável.

### P5. Médico tem login no sistema?
**Default:** Sim — médico tem entrada na tabela `users` (papel `medico`) vinculada via FK ao `doctors.user_id`. Recepcionista define email/senha temporária ao cadastrar o médico.

### P6. Remarcar é uma ação atômica ou cancela + cria?
**Default:** Atômica (`PATCH /appointments/{id}` mudando `datetime`). Mantém o ID e histórico, simplifica para o paciente. Mas mudamos `status` para `agendada` (continua) e gravamos `rescheduled_at` no banco para auditoria.

### P7. Granularidade dos slots de horário
**Default:** 30 minutos fixos. Janela de atendimento do médico é definida em blocos de 30min (ex: seg-sex 08:00–12:00 e 14:00–18:00).

### P8. Antecedência mínima para agendar / cancelar
**Default:** Agendar com no mínimo **1 hora** de antecedência. Cancelar até **30 minutos** antes. Validações ficam no service e geram cenários ricos de teste.

### P9. Um paciente pode ter 2 consultas no mesmo horário (com médicos diferentes)?
**Default:** Não — regra de negócio bloqueia. Gera 409 Conflict. Bom cenário de teste.

### P10. Notas clínicas do médico são visíveis ao paciente?
**Default:** Não. Apenas o médico e recepcionistas veem. Paciente vê só status + médico + horário.

### P11. Precisa de paginação nas listagens?
**Default:** Versão simples por enquanto: sem paginação, mas com filtros de query (`?status=agendada&from=&to=`). Limite implícito de 200 registros.

### P12. CPF é obrigatório no cadastro de paciente?
**Default:** Não obrigatório no MVP — apenas `name`, `email`, `password`, `phone` (opcional). CPF entra como campo opcional para enriquecer cenários de validação se houver tempo.
