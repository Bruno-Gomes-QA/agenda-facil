<script setup lang="ts">
import type { Specialty } from '~/types/specialty'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const items = ref<Specialty[]>([])
const loading = ref(true)
const errorMsg = ref('')

const showForm = ref(false)
const editing = ref<Specialty | null>(null)
const form = reactive({ name: '', description: '' })

async function load() {
  loading.value = true
  try {
    items.value = await useSpecialties().list(true)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate() {
  editing.value = null
  form.name = ''
  form.description = ''
  showForm.value = true
}
function openEdit(s: Specialty) {
  editing.value = s
  form.name = s.name
  form.description = s.description ?? ''
  showForm.value = true
}

async function submit() {
  errorMsg.value = ''
  try {
    const api = useSpecialties()
    if (editing.value) {
      await api.update(editing.value.id, { name: form.name, description: form.description || null })
    } else {
      await api.create({ name: form.name, description: form.description || null })
    }
    showForm.value = false
    await load()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function toggleActive(s: Specialty) {
  try {
    if (s.is_active) await useSpecialties().remove(s.id)
    else await useSpecialties().update(s.id, { is_active: true })
    await load()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Especialidades</h1>
      <button @click="openCreate" class="btn-primary">+ Nova</button>
    </div>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
      {{ errorMsg }}
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <table v-else class="w-full bg-white rounded-xl overflow-hidden shadow-sm">
      <thead class="bg-gray-50 text-xs uppercase text-gray-500">
        <tr><th class="text-left px-4 py-3">Nome</th><th class="text-left px-4 py-3">Descrição</th><th class="px-4 py-3">Status</th><th class="px-4 py-3">Ações</th></tr>
      </thead>
      <tbody>
        <tr v-for="s in items" :key="s.id" class="border-t border-gray-100">
          <td class="px-4 py-3 font-medium">{{ s.name }}</td>
          <td class="px-4 py-3 text-sm text-gray-600">{{ s.description || '—' }}</td>
          <td class="px-4 py-3 text-center">
            <span :class="['text-xs px-2 py-0.5 rounded-full', s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
              {{ s.is_active ? 'ativa' : 'inativa' }}
            </span>
          </td>
          <td class="px-4 py-3 text-center text-sm whitespace-nowrap">
            <button @click="openEdit(s)" class="text-brand-600 hover:underline mr-3">editar</button>
            <button @click="toggleActive(s)" class="text-gray-500 hover:underline">
              {{ s.is_active ? 'desativar' : 'reativar' }}
            </button>
          </td>
        </tr>
        <tr v-if="items.length === 0"><td colspan="4" class="text-center py-8 text-gray-400">Nenhuma especialidade.</td></tr>
      </tbody>
    </table>

    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" @click.self="showForm = false">
      <form @submit.prevent="submit" class="bg-white rounded-2xl p-6 w-full max-w-md space-y-4">
        <h2 class="text-lg font-bold">{{ editing ? 'Editar' : 'Nova' }} especialidade</h2>
        <div>
          <label class="field-label">Nome</label>
          <input v-model="form.name" class="input-field" required maxlength="80" />
        </div>
        <div>
          <label class="field-label">Descrição</label>
          <textarea v-model="form.description" rows="3" class="input-field" />
        </div>
        <div class="flex gap-2 justify-end">
          <button type="button" @click="showForm = false" class="px-4 py-2 text-gray-600">Cancelar</button>
          <button type="submit" class="btn-primary">Salvar</button>
        </div>
      </form>
    </div>
  </section>
</template>
