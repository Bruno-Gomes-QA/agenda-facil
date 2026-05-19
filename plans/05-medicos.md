# Etapa 5 — Cadastro de Médicos

> Recepcionista cadastra médico: cria simultaneamente o `users` (papel `medico`) e o `doctors` vinculado.

---

## 1. Migration

Cria `doctors` conforme schema. Não há seed adicional aqui (médicos demo entram via seed da etapa 2).

## 2. API

| Método | Path | Auth |
|---|---|---|
| GET | `/doctors` | Público (resumido) |
| GET | `/doctors/{id}` | Público (resumido) |
| POST | `/doctors` | Recepcionista |
| PATCH | `/doctors/{id}` | Recepcionista |
| DELETE | `/doctors/{id}` | Recepcionista (soft: `is_active=false`) |

### Filtros em GET /doctors
`?specialty_id=&search=&include_inactive=false`
- `search` busca em `name` (LIKE case-insensitive) e `crm`.

### Schemas
```python
class DoctorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)        # senha temporária
    phone: str | None = None
    specialty_id: int
    crm: str = Field(pattern=r"^\d{4,6}-[A-Z]{2}$")  # ex: 12345-SP
    bio: str | None = None

class DoctorUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    specialty_id: int | None = None
    bio: str | None = None
    is_active: bool | None = None

class DoctorOut(BaseModel):
    id: int
    name: str
    email: EmailStr            # exposto só para staff/médico — ver P3
    crm: str
    bio: str | None
    is_active: bool
    specialty: SpecialtyOut

class DoctorPublicOut(BaseModel):  # versão pública (sem email)
    id: int
    name: str
    crm: str
    bio: str | None
    specialty: SpecialtyOut
```

### Service
- `create_doctor`: transação SQL — cria `users` (role=`medico`), cria `doctors` apontando para esse user. Valida unicidade de CRM e email.
- `update_doctor`: nunca muda `user_id` nem `crm` (CRM é imutável).
- Deletar: soft delete + valida sem consultas futuras agendadas (se houver, retornar 409 com lista para forçar recepcionista a cancelar primeiro).

### Erros
- CRM duplicado → 409.
- Especialidade inválida ou inativa → 422.
- Email duplicado (usuário) → 409.

## 3. Frontend

### Rotas
- `/doctors` — pública, lista catálogo (busca por nome/especialidade).
- `/doctors/[id]` — pública, perfil do médico + botão "Agendar consulta" (leva ao fluxo da etapa 7).
- `/admin/doctors` — gestão (recepcionista).
- `/admin/doctors/new`
- `/admin/doctors/[id]/edit`

### Componentes
- `domain/doctors/DoctorCard.vue` (foto/iniciais, nome, especialidade, CRM).
- `domain/doctors/DoctorList.vue` (grid + filtros).
- `domain/doctors/DoctorForm.vue` (form com select de especialidade).
- `domain/doctors/DoctorFilters.vue` (search + select especialidade).

### Composables
- `useDoctorsList(filters)`, `useDoctorDetail(id)`, `useDoctorCreate`, `useDoctorUpdate`, `useDoctorDelete`.

### UX
- Lista pública mostra apenas `DoctorPublicOut`.
- Tela admin mostra também email (`DoctorOut`).
- Form de criação inclui "senha temporária" com botão "gerar aleatória".

## 4. Critérios de aceite (QA)

- [ ] CRM em formato inválido → 422.
- [ ] CRM duplicado → 409.
- [ ] Criar médico cria também `users` com role `medico`; médico consegue fazer login com a senha temporária.
- [ ] Listagem pública não expõe email do médico.
- [ ] Inativar médico com consulta futura agendada → 409 com lista de consultas afetadas.
- [ ] Reativar médico volta a aparecer no catálogo.
- [ ] Busca por nome parcial funciona case-insensitive.

## 5. Perguntas de refinamento

### P1. Formato de CRM?
**Default:** `NNNN[N[N]]-UF` (4 a 6 dígitos + traço + UF). Regex `^\d{4,6}-[A-Z]{2}$`. Simples mas válido.

### P2. CRM é imutável?
**Default:** Sim — em produção real CRM é identidade legal. Cenário ruim no QA é justamente tentar mudar e ver bloqueio.

### P3. Email do médico é público?
**Default:** Não — apenas `DoctorOut` (autenticado, qualquer papel) mostra. Lista pública usa `DoctorPublicOut`.

### P4. Foto do médico?
**Default:** **Fora do MVP**. UI usa iniciais geradas com cor estável.

### P5. Médico pode ter mais de uma especialidade?
**Default:** Não no MVP. Uma única FK `specialty_id`. Simplifica drasticamente.

### P6. Senha temporária é obrigatória ou opcional?
**Default:** Obrigatória. Recepcionista define e comunica ao médico fora do sistema. Sem fluxo de "primeira-troca-obrigatória" no MVP.

### P7. O que acontece com consultas passadas quando médico é inativado?
**Default:** Permanecem visíveis no histórico (consultas têm FK `RESTRICT`). Soft delete preserva tudo.
