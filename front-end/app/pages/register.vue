<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const auth = useAuthStore()
if (auth.isAuthenticated) {
  await navigateTo(auth.dashboardRoute())
}

const { register } = useAuthRegister()

const form = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
})
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  if (!form.name || !form.email || !form.password) {
    errorMsg.value = 'Preencha nome, e-mail e senha.'
    return
  }
  if (form.password.length < 6) {
    errorMsg.value = 'A senha deve ter pelo menos 6 caracteres.'
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    await register({
      name: form.name.trim(),
      email: form.email.trim(),
      password: form.password,
      phone: form.phone || undefined,
    })
    await navigateTo('/appointments')
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string }; status?: number }
    if (e?.status === 409) {
      errorMsg.value = 'Este e-mail já está cadastrado.'
    } else if (e?.data?.detail) {
      errorMsg.value = String(e.data.detail)
    } else {
      errorMsg.value = 'Erro ao criar conta. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-50 to-teal-50 p-6">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-xl p-8 md:p-10 animate-fade-slide">

      <!-- Cabeçalho -->
      <div class="flex items-center gap-3 mb-8">
        <AppLogo class="w-10 h-10 text-brand-600 animate-float" />
        <div>
          <h1 class="text-xl font-extrabold text-gray-900 leading-none">Criar Conta</h1>
          <p class="text-sm text-gray-400 mt-0.5">Agende consultas com facilidade</p>
        </div>
      </div>

      <!-- Alerta de erro -->
      <Transition name="slide-down">
        <div
          v-if="errorMsg"
          class="mb-5 flex items-start gap-3 bg-red-50 border border-red-200 text-red-700
                 rounded-xl px-4 py-3 text-sm"
        >
          <span class="shrink-0 mt-0.5">⚠️</span>
          <span>{{ errorMsg }}</span>
        </div>
      </Transition>

      <!-- Formulário -->
      <form @submit.prevent="handleSubmit" novalidate class="space-y-4">
        <div>
          <label for="name" class="field-label">Nome completo</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            autocomplete="name"
            placeholder="João da Silva"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <div>
          <label for="email" class="field-label">E-mail</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            placeholder="joao@email.com"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <div>
          <label for="password" class="field-label">Senha</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            placeholder="Mínimo 6 caracteres"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <div>
          <label for="phone" class="field-label">
            Telefone <span class="text-gray-400 font-normal">(opcional)</span>
          </label>
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            autocomplete="tel"
            placeholder="(11) 99999-9999"
            class="input-field"
            :disabled="loading"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="btn-primary w-full py-3 mt-2 flex items-center justify-center gap-2"
        >
          <svg v-if="loading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          {{ loading ? 'Criando conta…' : 'Criar conta' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        Já tem uma conta?
        <NuxtLink to="/login" class="text-brand-600 font-semibold hover:underline ml-1">
          Entrar
        </NuxtLink>
      </p>

    </div>
  </div>
</template>
