# Etapa 4 — Especialidades

> CRUD simples de especialidades médicas. Listagem é pública; mutação só por recepcionista.

---

## 1. Migration

Cria `specialties`. Seed insere 5 padrão (Clínico Geral, Cardiologia, Dermatologia, Pediatria, Ortopedia).

## 2. API

| Método | Path | Auth |
|---|---|---|
| GET | `/specialties` | Público |
| GET | `/specialties/{id}` | Público |
| POST | `/specialties` | Recepcionista |
| PATCH | `/specialties/{id}` | Recepcionista |
| DELETE | `/specialties/{id}` | Recepcionista (soft delete: `is_active=false`) |

### Schemas
```python
class SpecialtyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None

class SpecialtyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None

class SpecialtyOut(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
```

### Regras
- `name` único (case-insensitive) → 409 se duplicado.
- `DELETE` faz `is_active=false`. Não permite deletar se houver médicos ativos vinculados → 409.
- `GET /specialties?include_inactive=false` (default false).

## 3. Frontend

### Rotas
- `/admin/specialties` — lista + ações (recepcionista)
- `/admin/specialties/new`
- `/admin/specialties/[id]/edit`

### Componentes
- `domain/specialties/SpecialtyList.vue` (tabela com badges de status)
- `domain/specialties/SpecialtyForm.vue`

### Composables
- `useSpecialtiesList`, `useSpecialtyCreate`, `useSpecialtyUpdate`, `useSpecialtyDelete`

### UX
- Toast verde ao criar; modal de confirmação ao desativar.
- Inativos aparecem riscados em cinza, com filtro "mostrar inativos".

## 4. Critérios de aceite (QA)

- [ ] Criar especialidade com nome duplicado (case-insensitive) → 409.
- [ ] Paciente tenta `POST /specialties` → 403.
- [ ] Listagem pública não exige token.
- [ ] Inativar especialidade sem médicos: OK. Com médicos ativos: 409.
- [ ] Reativar especialidade volta a aparecer no select de cadastro de médico.

## 5. Perguntas de refinamento

### P1. Especialidade já cadastrada com nome em maiúsculo bate com minúsculo?
**Default:** Sim — comparação case-insensitive via `LOWER(name)`.

### P2. Permitir descrição em markdown?
**Default:** Não — texto puro. Simplifica.

### P3. Deletar fisicamente uma especialidade sem médicos?
**Default:** Não. Sempre soft delete para preservar histórico de consultas (mesmo que indireto via médico).

### P4. Especialidades vêm ordenadas como?
**Default:** Alfabético crescente.
