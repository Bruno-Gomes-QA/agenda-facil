# Etapa 7 — Agendamento (paciente)

> Paciente logado: agenda nova consulta, vê suas consultas, remarca, cancela.

---

## 1. Migration

Cria `appointments` e `appointment_history`.

## 2. API (escopo do paciente nesta etapa)

| Método | Path | Auth | Descrição |
|---|---|---|---|
| POST | `/appointments` | Paciente | Cria consulta para si (sem `patient_id` no body) |
| GET | `/appointments/me` | Paciente | Lista próprias consultas (filtros: `status`, `from`, `to`) |
| GET | `/appointments/{id}` | Dono ou staff | Detalhe |
| PATCH | `/appointments/{id}` | Dono ou staff | Remarcar (muda `scheduled_at`) |
| DELETE | `/appointments/{id}` | Dono ou staff | Cancelar (soft: `status=cancelada`) |

### Schemas
```python
class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_at: datetime    # ISO 8601 com TZ
    reason: str | None = Field(default=None, max_length=255)

class AppointmentUpdate(BaseModel):
    scheduled_at: datetime    # remarcação

class AppointmentOut(BaseModel):
    id: int
    patient: UserOut
    doctor: DoctorPublicOut
    scheduled_at: datetime
    duration_min: int
    status: Literal['agendada', 'cancelada', 'realizada', 'no_show']
    reason: str | None
    created_at: datetime
    rescheduled_at: datetime | None
    cancelled_at: datetime | None
```

### Regras de service (`create_appointment`)
1. Valida médico ativo (404 se não existe / 409 se inativo).
2. Valida `scheduled_at`:
   - É um slot exato (alinhado a 30min) → 422.
   - Está dentro de uma janela de disponibilidade do médico → 422 "fora do horário de atendimento".
   - Respeita lead time (>= agora + 60min) → 422.
   - Não pode ser no passado → 422.
3. Não pode haver outra consulta `agendada` para esse `(doctor_id, scheduled_at)` → 409 (também garantido por índice único).
4. Paciente não pode ter outra consulta `agendada` no mesmo `scheduled_at` (qualquer médico) → 409.
5. Cria + grava em `appointment_history` (status `null → agendada`).

### `update_appointment` (remarcar)
- Só permite se `status='agendada'` (outros → 409).
- Aplica mesmas validações de horário.
- Atualiza `scheduled_at` + `rescheduled_at=now()`.
- Cria entrada em `appointment_history`.

### `cancel_appointment`
- Só se `status='agendada'`.
- Aplica antecedência mínima de cancelamento: **30 min antes**. Caso contrário 409 "fora do prazo de cancelamento" (recepcionista pode forçar — ver etapa 8).
- Seta `status='cancelada'`, `cancelled_at=now()`, `cancelled_by=current_user.id`.
- Grava no histórico.

### Autorização
- Paciente só pode operar consultas onde `patient_id == current_user.id`.
- Tentativa em consulta de outro → 404 (não vazar existência).

## 3. Frontend

### Rotas
- `/appointments` — lista (com tabs: "Próximas" / "Histórico").
- `/appointments/new?doctor_id=` — fluxo de novo agendamento.
- `/appointments/[id]` — detalhe + ações (remarcar/cancelar).

### Fluxo "Nova consulta"
1. Acessou via card do médico (etapa 5) ou pelo botão "+ Nova consulta" em `/appointments`.
2. Se não veio do médico, primeiro escolhe especialidade → médico.
3. Calendário (shadcn `Calendar`) — só permite datas futuras dentro de 60 dias.
4. Ao escolher data, carrega `SlotPicker` com horários do dia.
5. Campo opcional "motivo".
6. Dialog de confirmação com resumo → confirma.
7. Redireciona para `/appointments/[id]` com toast "consulta agendada".

### Componentes
- `domain/appointments/AppointmentCard.vue`
- `domain/appointments/AppointmentList.vue` (tabs + filtros)
- `domain/appointments/AppointmentForm.vue`
- `domain/appointments/AppointmentDetail.vue`
- `domain/appointments/CancelDialog.vue`
- `domain/appointments/RescheduleDialog.vue`

### Composables
- `useMyAppointments(filters)`, `useAppointmentDetail(id)`
- `useAppointmentCreate()`, `useAppointmentUpdate(id)`, `useAppointmentCancel(id)`

### UX
- Status com badges coloridos: agendada (azul), realizada (verde), cancelada (cinza), no_show (vermelho).
- Botões "Remarcar"/"Cancelar" só aparecem se `status='agendada'` e dentro de janela.
- Mensagens amigáveis em PT-BR para cada erro 409/422 da API.

## 4. Critérios de aceite (QA)

- [ ] Paciente agenda em slot livre → 201.
- [ ] Mesmo slot tentado por outro paciente → 409.
- [ ] Slot fora da janela do médico → 422.
- [ ] Slot com menos de 60min de antecedência → 422.
- [ ] Data no passado → 422.
- [ ] Remarcar consulta cancelada → 409.
- [ ] Cancelar 20 min antes da consulta → 409 "fora do prazo".
- [ ] Cancelar 1h antes → 200.
- [ ] Paciente A tenta ver consulta do paciente B → 404.
- [ ] Histórico (`appointment_history`) registra cada transição.
- [ ] Após cancelar, slot volta a aparecer em `GET availability`.

## 5. Perguntas de refinamento

### P1. Paciente pode cancelar a qualquer momento ou tem prazo?
**Default:** 30 min de antecedência. Recepcionista ignora esse limite (etapa 8). Gera cenários de teste.

### P2. Remarcar é livre quantas vezes?
**Default:** Sim, sem limite. Apenas atualiza `rescheduled_at` (sobrescreve com a última).

### P3. Permitir "consulta retroativa" pela recepcionista (cadastrar consulta passada já realizada)?
**Default:** **Não no MVP**. Sempre `scheduled_at > now()`. Simplifica.

### P4. Paciente vê consultas canceladas?
**Default:** Sim — aba "Histórico" mostra realizadas, canceladas e no_show.
R: O paciente consegue visualizar apenas o próprio histórico de consultas. Já a recepcionista possui acesso ao histórico geral, incluindo consultas realizadas, canceladas e no-show.

### P5. Tela do paciente exibe `doctor_notes`?
**Default:** Não. Notas clínicas são privadas (médico/recepcionista). Cenário de teste: garantir que API não retorna `doctor_notes` para o paciente.

### P6. O que aparece no card de uma consulta agendada hoje?
**Default:** Nome do médico, especialidade, data/hora formatada em PT-BR, motivo, status, e botões "Remarcar" / "Cancelar".

### P7. Confirmação visual para cancelar?
**Default:** Sim — dialog "Tem certeza? Esta ação não pode ser desfeita." com botões Confirmar/Voltar.

### P8. Limite de consultas futuras simultâneas por paciente?
**Default:** Sem limite no MVP. Bom cenário de stress no teste.
