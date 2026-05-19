# Etapa 3 — Autenticação e Usuários

> Cadastro público de paciente, login JWT para os 3 papéis, `/me`, criação de staff (recepcionista/médico) por recepcionista.

---

## 1. Migration

Cria `users` e `patients` conforme `02-schema-banco.md`.
Seed cria 1 recepcionista admin + 1 paciente demo.

## 2. API

### Endpoints
| Método | Path | Auth | Quem |
|---|---|---|---|
| POST | `/users` | — | Público — cria **paciente** |
| POST | `/users/staff` | Bearer | Recepcionista — cria recepcionista ou médico |
| POST | `/auth/login` | — | Todos |
| GET | `/auth/me` | Bearer | Todos |
| POST | `/auth/logout` | Bearer | Todos (token-stateless: cliente descarta) |
| GET | `/users/{id}` | Bearer | Próprio usuário ou recepcionista |

### Schemas Pydantic (essenciais)
```python
class PatientCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None

class StaffCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal['recepcionista', 'medico']
    phone: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Literal['paciente', 'recepcionista', 'medico']
    phone: str | None
    is_active: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
```

### Regras de service
- `create_patient`: hash bcrypt; email único (409 se duplicado); cria linha em `patients` se vier CPF/birth_date.
- `create_staff`: só recepcionista pode chamar (RBAC via `Depends(require_role('recepcionista'))`).
- `login`: valida senha; gera JWT com `sub=user.id` e `role`; expira em 8h.
- `get_current_user`: dependency que decodifica JWT, busca usuário, valida `is_active=True`.
- `require_role(*roles)`: helper que recebe `get_current_user` e checa role.

### Erros
- Email duplicado → 409.
- Login inválido → 401 "credenciais inválidas".
- Token inválido/expirado → 401.
- Tentativa de staff sem permissão → 403.

## 3. Frontend

### Rotas
- `/login` — pública (form email/senha)
- `/register` — pública (auto-cadastro paciente)
- `/admin/staff/new` — protegida (apenas recepcionista) — cria recepcionista/médico

### Componentes
- `domain/auth/LoginForm.vue`
- `domain/auth/RegisterPatientForm.vue`
- `domain/auth/StaffForm.vue`

### Composables
- `composables/api/auth/useAuthLogin.ts`
- `composables/api/auth/useAuthRegister.ts`
- `composables/api/auth/useAuthMe.ts`
- `composables/api/users/useStaffCreate.ts`

### Store
- `stores/auth.ts`: `accessToken` em memória + `user` reativo. Persistir em `sessionStorage` (não localStorage) para sobreviver a F5 mas não sessão de navegador.

### Middleware
- `middleware/auth.ts` — redireciona não autenticado para `/login`.
- `middleware/role.ts` — recebe roles aceitos via `definePageMeta({ requiredRoles: ['recepcionista'] })`.

### Redirecionamento pós-login
- `paciente` → `/appointments`
- `recepcionista` → `/admin`
- `medico` → `/doctor/agenda`

## 4. Critérios de aceite (QA)

- [ ] Cadastro público cria paciente; tentar com email duplicado retorna 409.
- [ ] Senha < 6 caracteres falha com 422.
- [ ] Login com senha errada → 401.
- [ ] Token expirado é rejeitado.
- [ ] Paciente não consegue chamar `POST /users/staff` (403).
- [ ] FE redireciona conforme papel após login.
- [ ] F5 em página protegida mantém usuário logado (via sessionStorage).
- [ ] Logout limpa store e redireciona para `/login`.

## 5. Perguntas de refinamento

### P1. JWT em memória ou cookie httpOnly?
**Default:** **Em memória + sessionStorage** (mais simples e suficiente para QA). Cookie httpOnly seria mais seguro mas exige CSRF token e complica.

### P2. Duração do token?
**Default:** 8 horas. Sem refresh token no MVP.

### P3. Senha mínima?
**Default:** 6 caracteres. Sem regra de complexidade — facilita testes manuais; gera cenários de validação na borda.

### P4. Recepcionista pode criar paciente também (não só staff)?
**Default:** Sim — endpoint separado `POST /admin/patients` que aceita os mesmos campos de `PatientCreate` + permite pular `password` (gera senha temporária). Útil para o fluxo "agendar por telefone". (Detalhado na etapa 8.)

### P5. Email é case-sensitive?
**Default:** Não — normaliza para lowercase no service antes de salvar/buscar.

### P6. Bloqueio após N tentativas erradas?
**Default:** Não no MVP. Só feedback genérico "credenciais inválidas".

### P7. Recuperação de senha?
**Default:** **Fora do MVP**. Recepcionista pode resetar senha via `PATCH /users/{id}/password` (etapa de extensão se sobrar tempo).

### P8. Médico cadastrado por recepcionista pode trocar a própria senha depois?
**Default:** Sim — endpoint `PATCH /auth/me/password` autenticado, comum a todos os papéis.
