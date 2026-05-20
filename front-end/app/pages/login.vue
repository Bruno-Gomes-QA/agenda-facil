<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const auth = useAuthStore()
if (auth.isAuthenticated) {
  await navigateTo(auth.dashboardRoute())
}

const { login } = useAuthLogin()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  if (!email.value || !password.value) {
    errorMsg.value = 'Preencha e-mail e senha.'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await login(email.value.trim(), password.value)
    // Redireciona com base no papel
    await navigateTo(auth.dashboardRoute())
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string }; status?: number }
    if (e?.status === 401 || e?.data?.detail) {
      errorMsg.value = 'E-mail ou senha incorretos.'
    } else {
      errorMsg.value = 'Erro ao conectar com o servidor. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}

function fillDemo(preset: { email: string; password: string }) {
  email.value = preset.email
  password.value = preset.password
}

const demoUsers = [
  { label: 'Recepção', email: 'admin@agendafacil.local', password: 'admin123', icon: '🧑‍💼' },
  { label: 'Dr. House', email: 'dr.house@agendafacil.local', password: 'house123', icon: '🩺' },
  { label: 'Paciente', email: 'paciente@agendafacil.local', password: 'paciente123', icon: '👤' },
]

const features = [
  { icon: '📅', title: 'Agendamento Online', desc: 'Marque consultas a qualquer hora, de qualquer lugar.' },
  { icon: '🔔', title: 'Lembretes Automáticos', desc: 'Nunca mais esqueça uma consulta marcada.' },
  { icon: '🩺', title: 'Múltiplas Especialidades', desc: 'Cardiologia, ortopedia, pediatria e muito mais.' },
]
</script>

<template>
  <div class="min-h-screen flex overflow-hidden">

    <!-- ─── PAINEL ESQUERDO ─── -->
    <div class="hidden lg:flex w-[52%] relative flex-col justify-between
                bg-gradient-to-br from-sky-900 via-sky-700 to-teal-600 p-12 overflow-hidden">

      <!-- Círculos decorativos -->
      <div class="absolute -top-20 -left-20 w-72 h-72 rounded-full bg-white/5 animate-spin-slow" />
      <div class="absolute top-1/3 -right-16 w-56 h-56 rounded-full bg-white/5 animate-float" />
      <div class="absolute bottom-8 left-1/3 w-40 h-40 rounded-full bg-white/5 animate-pulse-slow" />

      <!-- Marca -->
      <div class="relative z-10 flex items-center gap-3 animate-fade-slide">
        <AppLogo class="w-12 h-12 text-white drop-shadow-lg" />
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight leading-none">Agenda Fácil</h1>
          <p class="text-sky-200 text-sm mt-0.5 font-medium">Saúde sem complicação</p>
        </div>
      </div>

      <!-- Cards de features -->
      <div class="relative z-10 space-y-4">
        <div
          v-for="(feat, i) in features"
          :key="feat.title"
          :style="{ animationDelay: `${i * 120}ms` }"
          class="flex items-start gap-4 bg-white/10 backdrop-blur-sm rounded-2xl p-4 animate-fade-slide"
        >
          <span class="text-2xl">{{ feat.icon }}</span>
          <div>
            <p class="text-white font-semibold text-sm leading-none mb-1">{{ feat.title }}</p>
            <p class="text-sky-200 text-xs leading-relaxed">{{ feat.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Rodapé esquerdo -->
      <p class="relative z-10 text-sky-300 text-xs animate-fade-slide" style="animation-delay:400ms">
        © {{ new Date().getFullYear() }} Agenda Fácil · BUGBUSTERS
      </p>
    </div>

    <!-- ─── PAINEL DIREITO ─── -->
    <div class="flex-1 flex items-center justify-center bg-white p-8">
      <div class="w-full max-w-md animate-fade-slide">

        <!-- Logo mobile -->
        <div class="flex items-center gap-2.5 mb-8 lg:hidden">
          <AppLogo class="w-9 h-9 text-brand-600" />
          <span class="text-xl font-bold text-gray-900 tracking-tight">Agenda Fácil</span>
        </div>

        <h2 class="text-2xl font-extrabold text-gray-900 mb-1">Bem-vindo de volta</h2>
        <p class="text-sm text-gray-500 mb-8">Acesse sua conta para continuar</p>

        <!-- Alerta de erro -->
        <Transition name="slide-down">
          <div
            v-if="errorMsg"
            class="mb-5 flex items-start gap-3 bg-red-50 border border-red-200 text-red-700
                   rounded-xl px-4 py-3 text-sm"
          >
            <span class="mt-0.5 shrink-0">⚠️</span>
            <span>{{ errorMsg }}</span>
          </div>
        </Transition>

        <!-- Formulário -->
        <form @submit.prevent="handleSubmit" novalidate class="space-y-4">
          <div>
            <label for="email" class="field-label">E-mail</label>
            <input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="seu@email.com"
              class="input-field"
              :disabled="loading"
            />
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label for="password" class="field-label !mb-0">Senha</label>
              <NuxtLink to="/forgot-password" class="text-xs text-brand-600 hover:underline">
                Esqueceu a senha?
              </NuxtLink>
            </div>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••"
                class="input-field pr-11"
                :disabled="loading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <button type="submit" :disabled="loading" class="btn-primary w-full py-3 mt-2 flex items-center justify-center gap-2">
            <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ loading ? 'Entrando…' : 'Entrar' }}
          </button>
        </form>

        <p class="mt-5 text-center text-sm text-gray-500">
          Não tem uma conta?
          <NuxtLink to="/register" class="text-brand-600 font-semibold hover:underline ml-1">
            Criar conta
          </NuxtLink>
        </p>

        <!-- Credenciais de demo para QA -->
        <div class="mt-8 rounded-2xl border border-dashed border-gray-200 bg-gray-50 p-4">
          <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 text-center">
            🔑 Credenciais de Demo
          </p>
          <div class="space-y-2">
            <button
              v-for="u in demoUsers"
              :key="u.email"
              type="button"
              @click="fillDemo(u)"
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white border border-gray-200
                     hover:border-brand-400 hover:bg-brand-50 transition-all text-left group"
            >
              <span class="text-lg">{{ u.icon }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold text-gray-700 group-hover:text-brand-700">{{ u.label }}</p>
                <p class="text-[10px] text-gray-400 truncate">{{ u.email }}</p>
              </div>
              <span class="text-xs text-gray-300 group-hover:text-brand-400 font-mono">→</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
