# Etapa 8 — Painel da recepcionista

> Recepcionista (operador) gerencia agendas, cadastra pacientes por telefone, agenda em nome deles, força cancelamentos.

---

## 1. Migration

Nenhuma nova — reaproveita tudo das etapas anteriores. Pode adicionar índice em `appointments(scheduled_at)` para a visão "agenda do dia" se sentir necessidade.

## 2. API

### Endpoints novos / estendidos
| Método | Path | Auth | Observação |
|---|---|---|---|
| POST | `/admin/patients` | Recepcionista | Cria paciente em nome de alguém (senha opcional) |
| GET | `/admin/patients?search=` | Recepcionista | Busca por nome/email/cpf/telefone |
| GET | `/appointments` | Recepcionista | Lista geral com filtros: `doctor_id`, `patient_id`, `status`, `from`, `to` |
| POST | `/appointments` | Recepcionista | Aceita `patient_id` no body (paciente comum nunca envia) |
| PATCH | `/appointments/{id}` | Recepcionista | Pode remarcar ignorando lead time (`force=true`) |
| DELETE | `/appointments/{id}` | Recepcionista | Cancela sempre — sem regra de antecedência |
| GET | `/admin/agenda?date=YYYY-MM-DD&doctor_id=` | Recepcionista | Visão "dia" com slots vazios + ocupados |

### Regras extras
- `POST /admin/patients` aceita `password: str | None`. Se ausente, gera string aleatória e devolve no response (mostra na tela uma vez).
- `POST /appointments` por recepcionista exige `patient_id` no body. Se ausente → 422.
- Recepcionista bypassa validações de lead time e prazo de cancelamento (não bypassa: conflito de slot, médico inativo, paciente inativo).

### Schemas (deltas)
```python
class AppointmentCreateAsStaff(AppointmentCreate):
    patient_id: int

class AdminAgendaSlot(BaseModel):
    datetime: datetime
    status: Literal['livre', 'ocupado', 'bloqueado']
    appointment: AppointmentOut | None
```

## 3. Frontend

### Layout
- Recepcionista tem layout `layouts/admin.vue` com sidebar:
  - Dashboard (cards: consultas hoje, médicos ativos, pacientes cadastrados)
  - Agenda do dia
  - Consultas (todas)
  - Pacientes
  - Médicos
  - Especialidades
  - Equipe (staff)

### Rotas
- `/admin` — dashboard
- `/admin/agenda` — agenda do dia (timeline por médico)
- `/admin/appointments` — listagem com filtros avançados
- `/admin/appointments/new` — agendar para paciente
- `/admin/patients` — listagem
- `/admin/patients/new` — cadastro rápido (gera senha)
- `/admin/patients/[id]` — detalhe + consultas do paciente

### Fluxo "Agendar por telefone"
1. Acessa `/admin/appointments/new`.
2. Busca paciente: campo combinado (digita nome/email/telefone → autocomplete).
3. Se não achar, clica "+ Novo paciente" → modal com form rápido (nome, email, telefone). Salva e usa.
4. Escolhe especialidade → médico → data → slot.
5. Confirma.

### Componentes
- `domain/admin/AgendaTimeline.vue` (linha do tempo por médico, slots clicáveis)
- `domain/admin/PatientPicker.vue` (autocomplete + criar inline)
- `domain/admin/QuickPatientForm.vue`
- `domain/admin/StatsCards.vue`

### Composables
- `useAdminAgenda(date, doctorId)`
- `useAdminPatients(search)`, `useAdminPatientCreate()`
- `useAdminAppointments(filters)`

### UX
- Confirmação especial ao cancelar consulta de outro paciente: "Você está cancelando uma consulta de [paciente]. Notificar o paciente é responsabilidade externa ao sistema." (texto ajuda QA).
- Agenda do dia: slots ocupados clicáveis → modal com detalhe da consulta.

## 4. Critérios de aceite (QA)

- [ ] Recepcionista cria paciente sem senha; response contém senha gerada.
- [ ] Recepcionista agenda para outro paciente passando `patient_id` → 201.
- [ ] Paciente comum tenta passar `patient_id` no body → ignorado / 403 (define-se: ignorado).
- [ ] Recepcionista cancela consulta a 5 min do horário → 200 (bypass).
- [ ] Paciente tenta o mesmo → 409.
- [ ] Agenda do dia mostra todos os slots da janela do médico, com status correto.
- [ ] Busca de paciente por trecho do nome retorna lista parcial.
- [ ] Dashboard mostra "Consultas hoje" igual ao SQL `COUNT WHERE date(scheduled_at)=today AND status='agendada'`.

## 5. Perguntas de refinamento

### P1. Recepcionista tem permissão total (incluindo deletar outro recepcionista)?
**Default:** Sim — modelo simples. Em prod teria "super-admin", aqui não. Inativar staff é permitido.

### P2. Cadastro rápido de paciente exige email?
**Default:** Sim — email é PK lógica de `users`. Se paciente não tem, recepcionista usa um placeholder (`telefone@semmail.local`). Cenário de teste interessante.

### P3. Recepcionista pode ver `doctor_notes`?
**Default:** Sim — equivalente a "secretária do consultório". Compartilha o nível de acesso clínico.

### P4. Visão de agenda: por médico, por dia, ou ambos?
**Default:** Tela única — escolhe data, e cada médico vira uma coluna/lista. Para MVP: dropdown de médico (1 por vez) + timeline. Multi-médico simultâneo fica fora.

### P5. Recepcionista pode editar dados pessoais de outros pacientes?
**Default:** Sim — `PATCH /admin/patients/{id}`. Para "atualizar telefone que digitou errado".

### P6. Auditoria de quem cancelou?
**Default:** Já capturado em `appointments.cancelled_by` + `appointment_history`. UI mostra no detalhe da consulta.

### P7. Bypass de lead time é silencioso ou exige `?force=true`?
**Default:** Recepcionista nunca precisa de `force` — backend simplesmente não aplica a regra para esse papel. Mais simples.
