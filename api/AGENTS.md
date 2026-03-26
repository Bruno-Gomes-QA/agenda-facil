# AGENTS.md — Agenda Fácil (API)

Este documento define **regras obrigatórias** para agentes (Codex, Gemini, Claude, etc...) contribuírem no projeto com consistência arquitetural e qualidade de código.

> **Objetivo:** manter uma API REST simples em Python com **FastAPI**, organizada por módulos funcionais, conectada a um banco **PostgreSQL**, com foco em clareza e facilidade de manutenção para fins acadêmicos.

---

## 0. Visão Geral do Projeto

**Agenda Fácil** é um sistema de agendamento de consultas médicas.

| Camada | Responsabilidade |
|---|---|
| **`api/` (este)** | API REST FastAPI com toda a lógica de negócio, operações CRUD e controle de agendamentos. Inclui as migrations do banco. |
| `frontend/` | Interface web em Vue.js / Nuxt 4 que consome esta API. |

**Grupo:** BUGBUSTERS — Vinicius, Bruno, Vitor, Camila.

---

## 1) Stack oficial

### Runtime / API
- Python `>= 3.11`
- FastAPI
- Uvicorn (servidor de desenvolvimento)
- Pydantic v2 (validação de dados e schemas)

### Banco de Dados
- PostgreSQL
- SQLAlchemy 2.x (ORM)
- Alembic (migrations)

### Ambiente
- Docker + Docker Compose (API + banco juntos)

### Testes / tooling
- Pytest (testes unitários e de integração)
- Ruff (lint/format)
- Postman ou Insomnia para testes manuais das rotas

---

## 2) Módulos do Sistema

O projeto é organizado em módulos funcionais simples, sem schemas separados no Postgres (tudo em `public`):

| Módulo | Responsabilidade |
|---|---|
| `users` | Cadastro e autenticação de pacientes/recepcionistas |
| `doctors` | Cadastro de médicos e especialidades |
| `appointments` | Agendamento, visualização, remarcação e cancelamento de consultas |
| `availability` | Consulta de horários disponíveis por médico |

### Regras
1. Cada módulo tem seus próprios models, schemas Pydantic e routers.
2. Um módulo pode importar models/serviços de outro diretamente — o projeto é simples e não exige contratos abstratos.
3. Evite duplicar lógica: se dois módulos precisam da mesma operação, extraia para um utilitário compartilhado.

---

## 3) Arquitetura: API simples em camadas

Cada módulo segue esta separação básica:

- **models.py**: modelo ORM (SQLAlchemy) que mapeia a tabela.
- **schemas.py**: schemas Pydantic para request/response.
- **service.py**: lógica de negócio e acesso ao banco.
- **router.py**: rotas FastAPI que chamam o service.

### Boas práticas
- Regras de negócio ficam em `service.py`, não no router.
- O router nunca acessa o banco diretamente — sempre via service.
- Schemas Pydantic são usados para validar entrada e serializar saída.

---

## 4) Estrutura de pastas

```txt
app/
  main.py                  # cria o app FastAPI e registra os routers
  core/
    config.py              # variáveis de ambiente (DATABASE_URL, SECRET_KEY)
    database.py            # engine e SessionLocal (SQLAlchemy)
    security.py            # hash de senha e geração de JWT
  modules/
    users/
      models.py            # tabela users
      schemas.py           # UserCreate, UserOut, UserLogin
      service.py           # lógica de cadastro, login, hash de senha
      router.py            # POST /users, POST /auth/login
    doctors/
      models.py            # tabela doctors + specialties
      schemas.py           # DoctorCreate, DoctorOut
      service.py           # CRUD de médicos e especialidades
      router.py            # GET/POST /doctors, GET /specialties
    appointments/
      models.py            # tabela appointments (status: agendada, cancelada, remarcada)
      schemas.py           # AppointmentCreate, AppointmentOut, AppointmentUpdate
      service.py           # criar, listar, cancelar, remarcar consultas
      router.py            # GET/POST/PATCH/DELETE /appointments
    availability/
      schemas.py           # AvailabilitySlot
      service.py           # calcula horários livres cruzando consultas agendadas
      router.py            # GET /doctors/{id}/availability
alembic/
  versions/                # arquivos de migration gerados
  env.py
docker-compose.yml
Dockerfile
pyproject.toml
README.md
```

---

## 5) Banco de dados e Migrations (Alembic)

- Um único Alembic na raiz (`alembic/`) para o banco PostgreSQL.
- Toda alteração de tabela deve gerar uma migration: `alembic revision --autogenerate -m "descrição"`.
- Nunca altere o banco diretamente sem criar a migration correspondente.
- Tabelas principais: `users`, `doctors`, `specialties`, `appointments`.

---

## 6) Padrões de código

### Schemas (Pydantic)
- Sempre usar schemas separados para entrada (`Create`/`Update`) e saída (`Out`/`Response`).
- Nunca retornar o model ORM diretamente no router — use sempre o schema de saída.

### Autenticação
- Senhas armazenadas com hash (`bcrypt` ou `passlib`).
- Autenticação via JWT (token Bearer).
- Proteger rotas sensíveis com `Depends(get_current_user)`.

### Nomenclatura
- Funções de service: `create_user`, `get_doctor_by_id`, `cancel_appointment`
- Schemas: `UserCreate`, `DoctorOut`, `AppointmentUpdate`
- Models ORM: `User`, `Doctor`, `Appointment`

---

## 7) Erros e validação

- Usar `HTTPException` do FastAPI para erros esperados (404, 400, 409, 401).
- Nunca retornar traceback ou mensagem de erro interno para o cliente.
- Validar regras de negócio no service antes de persistir no banco.

Exemplos de erros esperados:
- Horário já ocupado → `409 Conflict`
- Usuário não encontrado → `404 Not Found`
- Dados inválidos → `422 Unprocessable Entity` (automático pelo Pydantic)
- Token inválido/ausente → `401 Unauthorized`

---

## 8) Testes

### O que testar (foco no que será avaliado)
- Cadastro de paciente: dados obrigatórios e validação de campos inválidos.
- Verificação de disponibilidade: conflito de horários.
- Confirmação e cancelamento de consulta: atualização de status.
- Cadastro de médico: sem duplicidade.

### Padrão
- Unit tests para funções de service (sem banco — usar mocks).
- Integration tests para endpoints (usar `TestClient` do FastAPI com banco de teste).
- Fixtures de banco: banco PostgreSQL separado ou SQLite em memória para testes.

---

## 9) Regras para agentes

1. Toda mudança de tabela deve ter migration Alembic correspondente.
2. Nunca inserir lógica de negócio diretamente no router.
3. Ao criar um endpoint novo, criar também o schema de entrada e saída Pydantic.
4. Ao alterar um model ORM, atualizar schemas e testes afetados.
5. Respeitar o estilo definido no `pyproject.toml` (Ruff).
6. Atualizar o `README.md` se alterar como executar ou configurar o projeto.

---

## 10) Checklist (agente deve seguir antes de finalizar)

- [ ] Migration criada se houve alteração no banco
- [ ] Schema Pydantic de entrada e saída definidos
- [ ] Lógica no service, não no router
- [ ] Senha nunca armazenada em texto puro
- [ ] Endpoint protegido por autenticação quando necessário
- [ ] Testes escritos para o fluxo implementado

---

## 11) Fonte da verdade

Este arquivo é a **referência técnica principal** do projeto.
Em caso de dúvida sobre padrão a seguir, consulte este documento primeiro.
