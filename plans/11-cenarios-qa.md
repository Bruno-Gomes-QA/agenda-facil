# Etapa 11 — Catálogo de cenários de QA

> Levantamento de cenários de teste manual e automatizado. A aula é de QA, então este documento é tão importante quanto o código.

---

## 1. Estratégia geral

| Tipo | Onde | Ferramenta sugerida |
|---|---|---|
| Unit (API) | `api/tests/unit/` | `pytest` + mocks |
| Integration (API) | `api/tests/integration/` | `pytest` + `TestClient` + banco SQLite em memória ou Postgres dedicado |
| E2E (FE+API) | `front-end/tests/e2e/` | Playwright |
| Manual exploratório | Planilha / Notion | Markdown + Postman collection |

## 2. Cenários por módulo

### 2.1 Autenticação (etapa 3)

| # | Cenário | Esperado |
|---|---|---|
| A01 | Cadastro paciente com dados válidos | 201 + usuário criado |
| A02 | Cadastro com email duplicado | 409 |
| A03 | Cadastro com senha 5 caracteres | 422 |
| A04 | Cadastro com email mal formado | 422 |
| A05 | Login com credenciais corretas | 200 + token válido |
| A06 | Login com senha errada | 401 |
| A07 | Login com email inexistente | 401 (mesma msg) |
| A08 | `/auth/me` sem token | 401 |
| A09 | `/auth/me` com token expirado | 401 |
| A10 | `/auth/me` com token de usuário desativado | 401 |
| A11 | Paciente chamando `POST /users/staff` | 403 |
| A12 | Logout invalida sessão no FE | redireciona |

### 2.2 Especialidades (etapa 4)

| # | Cenário | Esperado |
|---|---|---|
| E01 | Criar especialidade nova | 201 |
| E02 | Criar com nome duplicado (case-insensitive) | 409 |
| E03 | Paciente tenta criar | 403 |
| E04 | Listar como visitante | 200 |
| E05 | Inativar especialidade com médico ativo | 409 |
| E06 | Inativar especialidade sem médicos | 200 |
| E07 | Reativar volta no select de cadastro de médico | OK |

### 2.3 Médicos (etapa 5)

| # | Cenário | Esperado |
|---|---|---|
| D01 | Cadastrar médico válido | 201 + `users` criado |
| D02 | CRM inválido formato | 422 |
| D03 | CRM duplicado | 409 |
| D04 | Email duplicado | 409 |
| D05 | Especialidade inválida | 422 |
| D06 | Médico criado consegue logar com senha temporária | 200 |
| D07 | Listagem pública não expõe email | OK |
| D08 | Tentar alterar CRM | 422 / 400 |
| D09 | Inativar médico com consulta futura | 409 |
| D10 | Busca por nome parcial case-insensitive | OK |

### 2.4 Disponibilidade (etapa 6)

| # | Cenário | Esperado |
|---|---|---|
| V01 | Definir janela seg 08:00–12:00 | 8 slots gerados |
| V02 | Definir end_time < start_time | 422 |
| V03 | Sobrepor duas janelas no mesmo dia | 409 |
| V04 | Listar slots hoje a partir de horário passado | só futuros + lead time |
| V05 | Slot ocupado some da lista | OK |
| V06 | Cancelar consulta libera slot | OK |
| V07 | Médico A não pode editar regras de médico B | 403 |
| V08 | Range > 60 dias | array vazio para datas além |

### 2.5 Agendamento paciente (etapa 7)

| # | Cenário | Esperado |
|---|---|---|
| P01 | Agendar slot livre | 201 |
| P02 | Mesmo slot, segundo paciente | 409 |
| P03 | Slot fora de janela | 422 |
| P04 | Slot no passado | 422 |
| P05 | Slot menos de 60min à frente | 422 |
| P06 | Slot não alinhado (08:15) | 422 |
| P07 | Médico inativo | 409 |
| P08 | Mesmo paciente, dois médicos, mesmo horário | 409 |
| P09 | Remarcar consulta agendada para outro slot livre | 200 |
| P10 | Remarcar consulta cancelada | 409 |
| P11 | Cancelar 2h antes | 200 |
| P12 | Cancelar 10 min antes | 409 |
| P13 | Paciente A acessa consulta do paciente B | 404 |
| P14 | Listar próprias consultas com filtro `status=agendada` | só agendadas |
| P15 | Histórico registra cada transição | OK |
| P16 | `doctor_notes` não aparece para paciente | OK |

### 2.6 Recepcionista (etapa 8)

| # | Cenário | Esperado |
|---|---|---|
| R01 | Criar paciente sem senha | 201 + senha gerada no response |
| R02 | Agendar para outro paciente | 201 |
| R03 | Cancelar 5 min antes (bypass) | 200 |
| R04 | Buscar paciente por trecho de nome | retorna parcial |
| R05 | Visualizar agenda do dia de um médico | slots livres + ocupados |
| R06 | Cancelar consulta de outro: gravou `cancelled_by` | OK |
| R07 | Paciente tenta passar `patient_id` no body | ignorado/403 |
| R08 | Dashboard "consultas hoje" bate com SQL | OK |

### 2.7 Médico (etapa 9)

| # | Cenário | Esperado |
|---|---|---|
| M01 | Listar agenda do dia | só consultas próprias |
| M02 | Médico A acessa consulta médico B | 404 |
| M03 | Marcar `realizada` em consulta agendada | 200 |
| M04 | Marcar `no_show` antes do horário | 422 |
| M05 | Reverter `realizada` → `agendada` | 409 |
| M06 | Editar notas após `realizada` | 200 |
| M07 | Recepcionista edita notas | 200 |
| M08 | Notas não aparecem para paciente | OK |

### 2.8 UI / Frontend

| # | Cenário | Esperado |
|---|---|---|
| U01 | Mensagens de erro em PT-BR amigáveis (sem raw da API) | OK |
| U02 | Skeleton aparece em listagens | OK |
| U03 | Empty state após fetch vazio | OK |
| U04 | F5 em página autenticada mantém sessão | OK |
| U05 | Tab pacientes não acessível por médico (role guard) | redireciona |
| U06 | Toast aparece em sucesso/erro de ações | OK |
| U07 | Confirmação obrigatória antes de cancelar | OK |
| U08 | Calendário não permite datas passadas | OK |
| U09 | Slots em formato `HH:MM` com TZ correto | OK |

## 3. Dados de teste padrão (após `make up-api`)

| Email | Senha | Papel |
|---|---|---|
| admin@agendafacil.local | admin123 | recepcionista |
| dr.house@agendafacil.local | house123 | medico (Clínico Geral) |
| dra.grey@agendafacil.local | grey123 | medico (Cardiologia) |
| paciente@agendafacil.local | paciente123 | paciente |

## 4. Postman / Insomnia collection

Plano: criar `qa/agenda-facil.postman_collection.json` com requests organizadas por módulo, variáveis de ambiente (`baseUrl`, `token`) e scripts de pre-request para auto-login.

## 5. Critérios para "fechar QA"

- [ ] Todos os cenários A01–U09 executados e documentados em planilha (PASS/FAIL).
- [ ] Bugs encontrados abertos como issues no GitHub com label `bug`.
- [ ] Smoke test E2E em Playwright cobre 3 fluxos principais (cadastrar→agendar paciente, recepcionista agendar por telefone, médico marcar realizada).

## 6. Perguntas de refinamento

### P1. Playwright entra no MVP?
**Default:** Apenas como "stretch" — focar primeiro em manual + Postman. Se sobrar tempo na aula, automatizar os 3 smokes.

### P2. Banco para testes da API?
**Default:** Postgres separado via `docker compose -f docker-compose.test.yml up` ou `pytest-postgresql`. SQLite quebraria o ENUM e o índice parcial. Vamos de Postgres.

### P3. Cobertura mínima de teste unitário?
**Default:** Não impor % no MVP. Cobrir as funções de service críticas: `create_appointment`, `cancel_appointment`, `list_slots`.

### P4. Mock de tempo nos testes (para lead time)?
**Default:** Usar `freezegun` no Pytest para congelar `datetime.now()` e testar bordas de lead time.

### P5. Critério de pronto por etapa?
**Default:** Etapa só é considerada "feita" quando passa todos os cenários do módulo correspondente neste documento.
