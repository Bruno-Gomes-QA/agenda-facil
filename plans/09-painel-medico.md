# Etapa 9 — Painel do médico

> Médico vê sua agenda do dia, marca consultas como realizadas/no_show, adiciona notas.

---

## 1. Migration

Nenhuma. `appointments.doctor_notes` já existe (etapa 7).

## 2. API

| Método | Path | Auth | Descrição |
|---|---|---|---|
| GET | `/appointments/doctor/me?date=YYYY-MM-DD` | Médico | Agenda do dia (default = hoje) |
| GET | `/appointments/doctor/me?from=&to=` | Médico | Range |
| PATCH | `/appointments/{id}/status` | Médico (dono da consulta) | Body: `{ status: 'realizada' \| 'no_show' }` |
| PATCH | `/appointments/{id}/notes` | Médico (dono) ou Recepcionista | Body: `{ doctor_notes: str }` |

### Regras
- Médico só vê/edita consultas onde `doctor.user_id == current_user.id`.
- Transição `agendada → realizada | no_show` apenas.
- Não pode "desfazer" status (realizada/no_show são finais). Recepcionista também não pode (mantém auditoria limpa).
- Notas podem ser editadas mesmo após status final (correções clínicas).
- Toda mudança grava em `appointment_history`.

### Schemas
```python
class AppointmentStatusUpdate(BaseModel):
    status: Literal['realizada', 'no_show']

class AppointmentNotesUpdate(BaseModel):
    doctor_notes: str = Field(max_length=4000)

class DoctorAgendaItem(BaseModel):
    id: int
    patient: PatientSummary  # nome, telefone, idade (calculada de birth_date)
    scheduled_at: datetime
    status: str
    reason: str | None
    doctor_notes: str | None
```

## 3. Frontend

### Layout
`layouts/doctor.vue` com header simples: nome do médico, link "Agenda", botão "Sair".

### Rotas
- `/doctor/agenda` — agenda do dia (default ao logar).
- `/doctor/agenda?date=` — outro dia.
- `/doctor/appointments/[id]` — detalhe + ações.
- `/doctor/availability` — edição da própria disponibilidade (etapa 6).

### Componentes
- `domain/doctor/DoctorDayAgenda.vue` — lista cronológica, agrupada (manhã/tarde).
- `domain/doctor/AppointmentRowDoctor.vue` — card com paciente, horário, motivo, ações.
- `domain/doctor/StatusActionMenu.vue` — botões "Realizada" / "Não compareceu".
- `domain/doctor/NotesEditor.vue` — textarea com salvar (debounce ou botão).

### Composables
- `useDoctorAgenda(date)`
- `useAppointmentSetStatus(id)`
- `useAppointmentSetNotes(id)`

### UX
- Topo: seletor de data (hoje / amanhã / outra via calendário).
- Cada consulta tem ações inline: ▷ Marcar realizada / ✕ Não compareceu.
- Clicando no card abre painel lateral com detalhes do paciente + campo de notas.
- Indicador visual: consulta em andamento (horário atual ± 30min) destacada.

## 4. Critérios de aceite (QA)

- [ ] Médico A não vê consultas do médico B (404 se tentar acessar por ID).
- [ ] Marcar consulta como `realizada` → 200; segundo PATCH para `agendada` → 409 (imutável).
- [ ] Marcar `no_show` em consulta futura (antes do horário) → 422 "não é possível marcar antes do horário".
- [ ] Editar notas em consulta `realizada` → 200 (permitido).
- [ ] Histórico registra status e nota separadamente.
- [ ] Recepcionista também consegue editar notas.

## 5. Perguntas de refinamento

### P1. Médico pode marcar `no_show` antes do horário?
**Default:** Não — só após `scheduled_at`. Antes disso, recepcionista cancela. Boa regra de QA.

### P2. Médico pode marcar `realizada` antes do horário?
**Default:** Permitir — clínica pode adiantar. Não tem por que bloquear.

### P3. Médico pode editar notas após `realizada`?
**Default:** Sim — médico pode complementar prontuário depois da consulta. Notas ficam editáveis para sempre.

### P4. Mostrar telefone do paciente para o médico?
**Default:** Sim — ajuda em ligações de urgência. Email também.

### P5. Idade do paciente é exibida?
**Default:** Sim, se `birth_date` estiver preenchido. Calculada no FE.

### P6. Histórico de consultas anteriores do mesmo paciente é visível?
**Default:** **Fora do MVP**. Se sobrar tempo, adicionar painel lateral "Consultas anteriores deste paciente com você".

### P7. Notificação de "próxima consulta começando"?
**Default:** Fora do MVP. UI apenas destaca visualmente.
