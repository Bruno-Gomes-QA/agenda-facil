<script setup lang="ts">
import type { Doctor, DoctorPublic } from '~/types/doctor'
import type { Specialty } from '~/types/specialty'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const doctors = ref<DoctorPublic[]>([])
const specialties = ref<Specialty[]>([])
const loading = ref(true)
const errorMsg = ref('')

const showForm = ref(false)
const editing = ref<Doctor | null>(null)
const form = reactive({
  name: '', email: '', password: '', phone: '', specialty_id: '', crm: '', bio: '',
})

async function load() {
  loading.value = true
  try {
    [doctors.value, specialties.value] = await Promise.all([
      useDoctors().list({ include_inactive: true }),
      useSpecialties().list(),
    ])
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', email: '', password: '', phone: '', specialty_id: '', crm: '', bio: '' })
  showForm.value = true
}
async function openEdit(d: DoctorPublic) {
  try {
    editing.value = await useDoctors().getFull(d.id)
    Object.assign(form, {
      name: editing.value.name,
      email: editing.value.email,
      password: '',
      phone: editing.value.phone ?? '',
      specialty_id: String(editing.value.specialty.id),
      crm: editing.value.crm,
      bio: editing.value.bio ?? '',
    })
    showForm.value = true
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function submit() {
  errorMsg.value = ''
  try {
    if (editing.value) {
      await useDoctors().update(editing.value.id, {
        name: form.name,
        phone: form.phone || undefined,
        specialty_id: Number(form.specialty_id),
        bio: form.bio || undefined,
      })
    } else {
      await useDoctors().create({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined,
        specialty_id: Number(form.specialty_id),
        crm: form.crm,
        bio: form.bio || undefined,
      })
    }
    showForm.value = false
    await load()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function toggleActive(d: DoctorPublic) {
  try {
    if (d.is_active) await useDoctors().remove(d.id)
    else await useDoctors().update(d.id, { is_active: true })
    await load()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Médicos</h1>
      <button @click="openCreate" class="btn-primary">+ Novo</button>
    </div>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <table v-else class="w-full bg-white rounded-xl overflow-hidden shadow-sm">
      <thead class="bg-gray-50 text-xs uppercase text-gray-500">
        <tr>
          <th class="text-left px-4 py-3">Nome</th>
          <th class="text-left px-4 py-3">Especialidade</th>
          <th class="text-left px-4 py-3">CRM</th>
          <th class="px-4 py-3">Status</th>
          <th class="px-4 py-3">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in doctors" :key="d.id" class="border-t border-gray-100">
          <td class="px-4 py-3 font-medium">{{ d.name }}</td>
          <td class="px-4 py-3 text-sm">{{ d.specialty.name }}</td>
          <td class="px-4 py-3 text-sm">{{ d.crm }}</td>
          <td class="px-4 py-3 text-center">
            <span :class="['text-xs px-2 py-0.5 rounded-full', d.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
              {{ d.is_active ? 'ativo' : 'inativo' }}
            </span>
          </td>
          <td class="px-4 py-3 text-center text-sm whitespace-nowrap">
            <button @click="openEdit(d)" class="text-brand-600 hover:underline mr-3">editar</button>
            <NuxtLink :to="`/admin/doctors/${d.id}`" class="text-brand-600 hover:underline mr-3">agenda</NuxtLink>
            <button @click="toggleActive(d)" class="text-gray-500 hover:underline">
              {{ d.is_active ? 'desativar' : 'reativar' }}
            </button>
          </td>
        </tr>
        <tr v-if="doctors.length === 0"><td colspan="5" class="text-center py-8 text-gray-400">Nenhum médico.</td></tr>
      </tbody>
    </table>

    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50 overflow-auto" @click.self="showForm = false">
      <form @submit.prevent="submit" class="bg-white rounded-2xl p-6 w-full max-w-lg space-y-3 my-auto">
        <h2 class="text-lg font-bold">{{ editing ? 'Editar médico' : 'Novo médico' }}</h2>
        <div>
          <label class="field-label">Nome</label>
          <input v-model="form.name" class="input-field" required />
        </div>
        <div class="grid sm:grid-cols-2 gap-3">
          <div>
            <label class="field-label">E-mail</label>
            <input v-model="form.email" type="email" class="input-field" :disabled="!!editing" required />
          </div>
          <div v-if="!editing">
            <label class="field-label">Senha</label>
            <input v-model="form.password" type="password" class="input-field" minlength="6" required />
          </div>
          <div>
            <label class="field-label">Telefone</label>
            <input v-model="form.phone" class="input-field" />
          </div>
          <div>
            <label class="field-label">CRM</label>
            <input v-model="form.crm" class="input-field" :disabled="!!editing" required />
          </div>
        </div>
        <div>
          <label class="field-label">Especialidade</label>
          <select v-model="form.specialty_id" class="input-field" required>
            <option value="">Selecione</option>
            <option v-for="s in specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div>
          <label class="field-label">Bio</label>
          <textarea v-model="form.bio" rows="3" class="input-field" />
        </div>
        <div class="flex gap-2 justify-end">
          <button type="button" @click="showForm = false" class="px-4 py-2 text-gray-600">Cancelar</button>
          <button type="submit" class="btn-primary">Salvar</button>
        </div>
      </form>
    </div>
  </section>
</template>
