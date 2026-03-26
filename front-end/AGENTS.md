# AGENTS.md — Agenda Fácil (Frontend)

Estas diretrizes orientam qualquer agente LLM que contribua com o frontend Nuxt localizado em `app/`. Use-as como referência principal.

---

## 0. Visão Geral do Projeto

**Agenda Fácil** é um sistema de agendamento de consultas médicas.

| Camada | Responsabilidade |
|---|---|
| `api/` | API REST FastAPI — fonte de todos os dados exibidos neste frontend. |
| **`front-end/` (este)** | Interface web (Nuxt 4 / Vue 3 / TypeScript) para agendamento de consultas. Consome exclusivamente a API REST. Não acessa banco de dados diretamente. |

**Grupo:** BUGBUSTERS — Vinicius, Bruno, Vitor, Camila.

**Regra crítica:** nunca invente um endpoint ou estrutura de resposta — consulte o `AGENTS.md` da `api/` para confirmar o contrato antes de implementar.

---

## 1. Stack oficial

- **Framework**: Nuxt 4 (Vue 3.5+ `<script setup>`), TypeScript estrito
- **CSS**: Tailwind CSS 3
- **UI**: shadcn-vue (componentes acessíveis e reutilizáveis)
- **Package Manager**: **bun** (obrigatório). Use `bun install`, `bun run dev`, `bun run build`. Para instalar componentes shadcn: `bunx --bun shadcn-vue@latest add <component>`. Nunca use npm neste projeto.
- **Aliases**: `~/` aponta para `app/`. Mantenha imports absolutos via `~/` para arquivos internos.
- **Estado/Fetch**: Utilize `useState`, `useFetch` e o composable `useApiFetch` para comunicação com o backend.
- **Base URL da API**: `http://localhost:8000` (desenvolvimento). Configurável via `NUXT_PUBLIC_API_BASE_URL` em `.env`.

---

## 2. Backend — Endpoints Disponíveis

A API segue o padrão REST. Consulte o `api/AGENTS.md` para a referência completa.

### Autenticação (`/auth`)

| Método | Path | Descrição | Auth |
|---|---|---|---|
| POST | `/users` | Cadastro de paciente | — |
| POST | `/auth/login` | Email + senha → access token | — |
| GET | `/auth/me` | Perfil do usuário autenticado | Bearer |
| POST | `/auth/logout` | Logout | Bearer |

### Usuários / Pacientes (`/users`)

| Método | Path | Descrição |
|---|---|---|
| POST | `/users` | Cadastrar usuário |
| GET | `/users/{id}` | Buscar usuário por ID |

### Médicos (`/doctors`)

| Método | Path | Descrição |
|---|---|---|
| GET | `/doctors` | Listar médicos |
| POST | `/doctors` | Cadastrar médico |
| GET | `/doctors/{id}` | Detalhe do médico |
| GET | `/specialties` | Listar especialidades |

### Consultas (`/appointments`)

| Método | Path | Descrição |
|---|---|---|
| GET | `/appointments` | Listar consultas do usuário |
| POST | `/appointments` | Agendar consulta |
| PATCH | `/appointments/{id}` | Remarcar consulta |
| DELETE | `/appointments/{id}` | Cancelar consulta |

### Disponibilidade (`/doctors/{id}/availability`)

| Método | Path | Descrição |
|---|---|---|
| GET | `/doctors/{id}/availability` | Consultar horários disponíveis |

### Schemas TypeScript (a partir dos Pydantic da API)

\`\`\`ts
// Autenticação
interface LoginRequest { email: string; password: string }
interface LoginResponse { access_token: string; token_type: string; user: UserOut }

// Usuários
interface UserCreate { name: string; email: string; password: string; phone?: string }
interface UserOut { id: number; name: string; email: string; phone?: string }

// Médicos
interface DoctorCreate { name: string; specialty_id: number; crm: string }
interface DoctorOut { id: number; name: string; crm: string; specialty: SpecialtyOut }
interface SpecialtyOut { id: number; name: string }

// Consultas
interface AppointmentCreate { doctor_id: number; datetime: string }
interface AppointmentOut { id: number; doctor: DoctorOut; datetime: string; status: string }
interface AppointmentUpdate { datetime: string }

// Disponibilidade
interface AvailabilitySlot { datetime: string; available: boolean }
\`\`\`

---

## 3. Estrutura de Pastas

\`\`\`
app/
├── app.vue                  # Root component
├── layouts/                 # Layouts (default, auth)
├── middleware/              # Route middleware (auth guard)
├── pages/                   # Rotas Nuxt (file-based routing)
│   ├── index.vue            # Home / redirect
│   ├── login.vue            # Página de login
│   ├── register.vue         # Cadastro de paciente
│   ├── appointments/        # Agendamentos (listar, novo, detalhe)
│   └── doctors/             # Listagem de médicos e especialidades
├── components/
│   ├── ui/                  # shadcn-vue components (via CLI)
│   └── domain/              # Componentes de domínio
│       ├── auth/            # LoginForm, RegisterForm
│       ├── appointments/    # AppointmentCard, AppointmentForm
│       └── doctors/         # DoctorList, DoctorCard
├── composables/
│   ├── api/                 # Hooks por módulo
│   │   ├── auth/            # useAuthLogin, useAuthMe, useAuthLogout
│   │   ├── appointments/    # useAppointmentsList, useAppointmentCreate, etc.
│   │   └── doctors/         # useDoctorsList, useAvailability
│   └── core/                # useApiFetch (fetch base com token)
├── stores/                  # Pinia (auth store)
├── types/                   # Tipos TypeScript por módulo
│   ├── auth.ts
│   ├── appointments.ts
│   └── doctors.ts
├── assets/                  # CSS global
├── public/                  # Arquivos estáticos
└── lib/                     # Helpers (cn, utils)
\`\`\`

---

## 4. Convenções de Código

1. **Nomeação**: `camelCase` para variáveis/funções; `PascalCase` para componentes Vue e types/interfaces.
2. **Script Setup**: Use `<script setup lang="ts">` com `defineProps`/`defineEmits` tipados.
3. **Estado global**: Use Pinia para dados do usuário autenticado (auth store).
4. **Fetch**:
   - Nunca chame `$fetch` diretamente em páginas — use `useApiFetch` para garantir headers, base URL e token.
   - `useApiFetch` deve injetar `Authorization: Bearer <token>` automaticamente quando autenticado.
   - Em caso de 401, redirecionar para `/login`.
5. **Composables de API**:
   - Um composable por operação principal (`useAppointmentCreate`, `useDoctorsList`, etc.).
   - Retorne `{ loading, error, data }` + função de execução.
6. **Componentização**: Prefira fragmentar componentes grandes em subpastas por domínio.
7. **UI shadcn-vue**: Use componentes de `app/components/ui/*` em vez de HTML puro quando houver equivalente.
8. **Tratamento de erro**:
   - Nunca exiba o erro bruto da API diretamente para o usuário.
   - Exiba feedback via toast ou mensagem inline amigável em português.
9. **Datas**: Use componentes de calendário do shadcn-vue para seleção de data/hora.

---

## 5. Fluxo para Criar uma Tela Nova

### Passo 1 — Tipos

1. Identifique os contratos da API (`api/AGENTS.md`).
2. Crie/atualize `app/types/<módulo>.ts`.

### Passo 2 — Composable de API

1. Crie em `app/composables/api/<módulo>/use<Operação>.ts`.
2. Use `useApiFetch` internamente.
3. Exponha `{ loading, error, data }` reativos + função de execução.

### Passo 3 — Componentes de Domínio

1. Crie em `app/components/domain/<feature>/`.
2. Subcomponentes separados por responsabilidade (form, list, card).

### Passo 4 — Página

1. Crie o arquivo em `app/pages/`.
2. No `<script setup>`: importe composables e stores.
3. Configure `definePageMeta` (middleware, layout).

---

## 6. Autenticação

### Store de Auth (`stores/auth.ts`)

- `accessToken: string | null` — armazenado em memória (não localStorage).
- `user: UserOut | null` — perfil do usuário autenticado.
- `isAuthenticated: computed(() => !!accessToken)`.
- Actions: `login()`, `logout()`, `fetchProfile()`.

### Middleware de Auth (`middleware/auth.ts`)

- Redireciona para `/login` se não autenticado.
- Aplique nas páginas que requerem autenticação via `definePageMeta({ middleware: 'auth' })`.

---

## 7. Padrões de UI/UX

### Formulários
- Labels sempre visíveis (não apenas placeholder).
- Validação inline com mensagens em português.
- Botão de submit desabilitado durante `loading`.
- Feedback de sucesso/erro via toast.

### Tabelas e Listas
- Exibir skeleton de carregamento enquanto dados são buscados.
- Empty state com mensagem clara quando a lista estiver vazia (apenas após o fetch concluir).

### Agendamento
- Seleção de data com componente de calendário do shadcn-vue.
- Horários disponíveis exibidos como botões selecionáveis.
- Confirmar agendamento antes de enviar (dialog de confirmação simples).

---

## 8. Checklist (agente deve seguir antes de finalizar)

- [ ] Tipos definidos em `app/types/<módulo>.ts`
- [ ] Composable de API encapsula `loading`, `error`, `data`
- [ ] UI usa componentes shadcn-vue
- [ ] Página protegida por middleware de auth quando necessário
- [ ] Erros exibidos de forma amigável (sem raw da API)
- [ ] Skeleton exibido durante carregamento
- [ ] Token nunca exposto em localStorage

---

## 9. Fonte da verdade

Este arquivo é a **referência técnica principal** do frontend.
Em caso de dúvida sobre contratos de API, consulte `api/AGENTS.md`.