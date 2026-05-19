# Etapa 10 — Frontend base (setup Nuxt + bun)

> Pacote único de "scaffolding" do FE. Tecnicamente precede o consumo das etapas 3–9, mas listado por último para não fragmentar o entendimento por funcionalidade.

---

## 1. Inicialização

```bash
cd front-end
bun create nuxt@latest .          # ou bunx nuxi init .
bun install
bunx --bun shadcn-vue@latest init
```

Tailwind: `bun add -D tailwindcss@3 postcss autoprefixer @nuxtjs/tailwindcss`
Componentes base: `bunx --bun shadcn-vue@latest add button input label form dialog dropdown-menu calendar select toast badge card table skeleton`

## 2. Configuração

### `nuxt.config.ts`
```ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    },
  },
  app: {
    head: { title: 'Agenda Fácil', htmlAttrs: { lang: 'pt-BR' } },
  },
})
```

### `.env`
```
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
> Funciona em WSL2 porque a API está exposta via `ports: ["8000:8000"]` no compose. `localhost` no WSL é o mesmo que `localhost` no Windows host.

## 3. `useApiFetch` (composable core)

```ts
// composables/core/useApiFetch.ts
export const useApiFetch: typeof useFetch = (request, opts = {}) => {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  return useFetch(request, {
    baseURL: config.public.apiBaseUrl,
    ...opts,
    headers: {
      ...(opts.headers || {}),
      ...(auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}),
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        auth.logout()
        navigateTo('/login')
      }
    },
  })
}
```

## 4. Store de auth (Pinia)

`stores/auth.ts` — `accessToken`, `user`, `login()`, `logout()`, `fetchProfile()`, hidratação em `app.vue` via `onMounted` lendo `sessionStorage`.

## 5. Layouts

- `layouts/default.vue` — site público (header com logo + "Entrar" / "Cadastrar").
- `layouts/auth.vue` — login/registro (centralizado, sem sidebar).
- `layouts/patient.vue` — paciente logado (header com "Minhas consultas", "Sair").
- `layouts/admin.vue` — recepcionista (sidebar).
- `layouts/doctor.vue` — médico (header simples).

Seletor automático via `definePageMeta({ layout: 'admin' })` ou middleware.

## 6. Middlewares

- `middleware/auth.global.ts` — hidrata token de `sessionStorage` e busca `/me` se ainda sem `user`.
- `middleware/role.ts` — bloqueia se role não bate com `definePageMeta({ requiredRoles })`.

## 7. Estrutura final (resumo)

```
front-end/
├── app/
│   ├── app.vue
│   ├── assets/css/main.css
│   ├── components/
│   │   ├── ui/                  # shadcn-vue
│   │   └── domain/{auth,doctors,appointments,specialties,admin,doctor,availability}/
│   ├── composables/
│   │   ├── core/useApiFetch.ts
│   │   └── api/{auth,doctors,specialties,appointments,availability}/
│   ├── layouts/{default,auth,patient,admin,doctor}.vue
│   ├── middleware/{auth.global,role}.ts
│   ├── pages/
│   ├── stores/auth.ts
│   ├── types/{auth,doctor,specialty,appointment,availability}.ts
│   └── lib/{cn,format,date}.ts
├── nuxt.config.ts
├── package.json
├── tailwind.config.ts
└── .env
```

## 8. Scripts (`package.json`)

```json
{
  "scripts": {
    "dev": "nuxt dev --port 3000",
    "build": "nuxt build",
    "preview": "nuxt preview",
    "typecheck": "nuxt typecheck"
  }
}
```

## 9. Como rodar

```bash
make up-db          # postgres
make up-api         # api + migrations
cd front-end && bun install && bun run dev
```

FE em `http://localhost:3000` consumindo `http://localhost:8000`.

## 10. Critérios de aceite (QA)

- [ ] `bun run dev` sobe sem erros.
- [ ] `bunx tsc --noEmit` sem erros.
- [ ] Página `/` carrega com layout default.
- [ ] Login funciona end-to-end com `useApiFetch`.
- [ ] 401 redireciona para `/login` automaticamente.
- [ ] F5 em página protegida não desloga.
- [ ] Build de produção (`bun run build`) finaliza sem erro.

## 11. Perguntas de refinamento

### P1. Versão do Nuxt?
**Default:** Nuxt 4 (latest stable). `bun create nuxt@latest`.

### P2. Pinia ou só `useState`?
**Default:** Pinia (já está pedido no AGENTS) — `@pinia/nuxt`.

### P3. Toasts: shadcn `toast` ou `sonner`?
**Default:** `sonner` (mais simples, single component). `bunx shadcn-vue add sonner`.

### P4. SSR ou SPA?
**Default:** SSR padrão do Nuxt — sem `ssr: false`. Como auth está em `sessionStorage`, garantir hidratação cliente no `app.vue`.

### P5. i18n?
**Default:** **Fora do MVP**. Todo o texto em PT-BR hard-coded.

### P6. Calendário: shadcn `Calendar` (vaul/v-calendar)?
**Default:** Componente shadcn-vue padrão (`@/components/ui/calendar`). Suporta date-picker.

### P7. Formatação de datas: lib?
**Default:** `date-fns` com locale pt-BR. `bun add date-fns`.
