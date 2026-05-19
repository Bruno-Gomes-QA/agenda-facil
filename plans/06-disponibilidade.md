# Etapa 6 — Disponibilidade do médico

> Janelas recorrentes por dia da semana + cálculo de slots livres em uma data específica, considerando consultas já agendadas.

---

## 1. Migration

Cria `doctor_availability_rules`.

## 2. Conceito

- Médico define **regras semanais recorrentes**: ex. seg-sex 08:00–12:00 e 14:00–18:00.
- Slots são **fatiados em blocos de 30min** (constante do sistema).
- API gera para uma data:
  1. Lista todos os slots da janela do dia da semana.
  2. Remove os slots ocupados por `appointments` com `status='agendada'` naquele dia.
  3. Remove slots no passado (se a data for hoje).
  4. Aplica antecedência mínima de 1 hora (default da etapa 7).

## 3. API

| Método | Path | Auth |
|---|---|---|
| GET | `/doctors/{id}/availability-rules` | Recepcionista, médico (próprio) |
| POST | `/doctors/{id}/availability-rules` | Recepcionista (ou médico no próprio) |
| DELETE | `/doctors/{id}/availability-rules/{rule_id}` | Recepcionista |
| GET | `/doctors/{id}/availability?date=YYYY-MM-DD` | Autenticado (qualquer papel) |
| GET | `/doctors/{id}/availability?from=YYYY-MM-DD&to=YYYY-MM-DD` | Autenticado |

### Schemas
```python
class AvailabilityRuleCreate(BaseModel):
    weekday: int = Field(ge=0, le=6)       # 0=segunda ... 6=domingo
    start_time: time
    end_time: time

class AvailabilityRuleOut(BaseModel):
    id: int
    weekday: int
    start_time: time
    end_time: time

class AvailabilitySlot(BaseModel):
    datetime: datetime
    available: bool   # sempre true na resposta (só listamos disponíveis); mas mantemos campo p/ debug

class AvailabilityResponse(BaseModel):
    doctor_id: int
    date: date
    slot_duration_min: int = 30
    slots: list[AvailabilitySlot]
```

### Service
```python
def list_slots(doctor_id, date):
    rules = repo.get_rules_for_weekday(doctor_id, date.weekday())
    slots = expand_rules_to_slots(rules, date, slot_min=30)
    busy = repo.get_busy_slots(doctor_id, date)  # status='agendada'
    return [s for s in slots if s not in busy and s > now()+min_lead_time]
```

### Validações
- `end_time > start_time`.
- Duas regras no mesmo `weekday` não podem se sobrepor → 409.
- `weekday` único? **Não** — médico pode ter 2 janelas no mesmo dia (manhã e tarde).

## 4. Frontend

### Rotas
- `/admin/doctors/[id]/availability` — recepcionista define regras.
- `/doctor/availability` — médico vê/edita as próprias.
- (Consumo da consulta de slots fica embutido no fluxo de agendamento — etapa 7.)

### Componentes
- `domain/availability/RulesEditor.vue` — tabela com 7 linhas (dias da semana) e múltiplos blocos por linha.
- `domain/availability/SlotPicker.vue` — recebe `doctorId` + `date`, exibe botões de horário (componente compartilhado).

### Composables
- `useAvailabilityRules(doctorId)`
- `useAvailabilityRuleCreate(doctorId)`
- `useAvailabilityRuleDelete(doctorId)`
- `useDoctorAvailability(doctorId, date)`

### UX
- `RulesEditor`: cada dia da semana tem um "+" para adicionar janela. Validação inline impede overlap.
- `SlotPicker`: skeleton enquanto carrega; "Sem horários disponíveis nesta data" como empty state.

## 5. Critérios de aceite (QA)

- [ ] Definir seg 08:00–12:00 mostra slots `08:00, 08:30, 09:00, ..., 11:30` (4h = 8 slots).
- [ ] Slot ocupado por consulta `agendada` some.
- [ ] Cancelar consulta libera o slot.
- [ ] Definir janela 12:00–08:00 → 422 (end <= start).
- [ ] Sobrepor 08:00–12:00 com 11:00–13:00 → 409.
- [ ] Buscar slots em data passada → array vazio.
- [ ] Hoje às 14:00, buscar slots de hoje a partir das 14:50 → não retorna 15:00 se lead-time = 60min; retorna 16:00+.

## 6. Perguntas de refinamento

### P1. Slots de 30min fixos ou configuráveis por médico?
**Default:** Fixos em 30min (constante no código). Coluna `appointments.duration_min` já existe para evoluir.

### P2. Suporte a feriados / bloqueios pontuais?
**Default:** **Fora do MVP**. Só janelas semanais recorrentes. Se houver tempo, adicionamos `doctor_blockout` (uma data específica indisponível) em etapa extra.

### P3. Quem pode editar disponibilidade do médico?
**Default:** Recepcionista (sempre) e o próprio médico (apenas a si mesmo). Médico não vê/edita de outros.

### P4. Lead time (antecedência mínima)?
**Default:** 60min para agendar (constante de sistema). Definido aqui pois a listagem de slots já aplica.

### P5. Janela máxima de busca?
**Default:** 60 dias à frente. Datas além disso retornam array vazio. Evita explosão de slots.

### P6. Se o médico mudar regras, consultas já agendadas fora da nova janela?
**Default:** Continuam válidas (não cancelam automaticamente). UI alerta o recepcionista quando vê a agenda. Bom cenário de QA.

### P7. GET availability com range (`from`/`to`)?
**Default:** Suportado, retorna `{ "YYYY-MM-DD": [slots...] }`. Útil para o calendário no FE pintar dias com disponibilidade.
