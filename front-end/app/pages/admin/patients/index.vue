<script setup lang="ts">
import type { UserOut } from '~/types/auth'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const patients = ref<UserOut[]>([])
const search = ref('')
const loading = ref(true)
const errorMsg = ref('')

const showForm = ref(false)
const form = reactive({ name: '', email: '', password: '', phone: '', cpf: '' })
const created = ref<{ user: UserOut; generated_password: string | null } | null>(null)

async function load() {
  loading.value = true
  try {
    patients.value = await useAdminPatients().list(search.value || undefined)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)
watch(search, () => load())

async function submit() {
  errorMsg.value = ''
  try {
    const res = await useAdminPatients().create({
      name: form.name,
      email: form.email,
      password: form.password || undefined,
      phone: form.phone || undefined,
      cpf: form.cpf || undefined,
    })
    created.value = res
    Object.assign(form, { name: '', email: '', password: '', phone: '', cpf: '' })
    await load()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Pacientes</h1>
      <button @click="showForm = !showForm; created = null" class="btn-primary">+ Novo</button>
    </div>

    <input v-model="search" placeholder="Buscar por nome ou e-mail…" class="input-field mb-4 max-w-md" />

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

    <div v-if="showForm" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
      <form @submit.prevent="submit" class="grid sm:grid-cols-2 gap-3">
        <div>
          <label class="field-label">Nome</label>
          <input v-model="form.name" class="input-field" required />
        </div>
        <div>
          <label class="field-label">E-mail</label>
          <input v-model="form.email" type="email" class="input-field" required />
        </div>
        <div>
          <label class="field-label">Senha (opcional — será gerada)</label>
          <input v-model="form.password" type="text" class="input-field" />
        </div>
        <div>
          <label class="field-label">Telefone</label>
          <input v-model="form.phone" class="input-field" />
        </div>
        <div>
          <label class="field-label">CPF</label>
          <input v-model="form.cpf" class="input-field" />
        </div>
        <div class="sm:col-span-2 flex justify-end gap-2">
          <button type="button" @click="showForm = false" class="px-4 py-2 text-gray-600">Cancelar</button>
          <button type="submit" class="btn-primary">Cadastrar</button>
        </div>
      </form>
      <div v-if="created?.generated_password" class="mt-4 bg-blue-50 border border-blue-200 text-blue-700 rounded-xl px-4 py-3 text-sm">
        Paciente <strong>{{ created.user.name }}</strong> criado. Senha temporária: <code class="font-mono">{{ created.generated_password }}</code>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <table v-else class="w-full bg-white rounded-xl overflow-hidden shadow-sm">
      <thead class="bg-gray-50 text-xs uppercase text-gray-500">
        <tr><th class="text-left px-4 py-3">Nome</th><th class="text-left px-4 py-3">E-mail</th><th class="text-left px-4 py-3">Telefone</th><th class="px-4 py-3">Status</th></tr>
      </thead>
      <tbody>
        <tr v-for="p in patients" :key="p.id" class="border-t border-gray-100">
          <td class="px-4 py-3 font-medium">{{ p.name }}</td>
          <td class="px-4 py-3 text-sm">{{ p.email }}</td>
          <td class="px-4 py-3 text-sm">{{ p.phone || '—' }}</td>
          <td class="px-4 py-3 text-center">
            <span :class="['text-xs px-2 py-0.5 rounded-full', p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
              {{ p.is_active ? 'ativo' : 'inativo' }}
            </span>
          </td>
        </tr>
        <tr v-if="patients.length === 0"><td colspan="4" class="text-center py-8 text-gray-400">Nenhum paciente.</td></tr>
      </tbody>
    </table>
  </section>
</template>
