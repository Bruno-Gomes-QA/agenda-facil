<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const items = ref<Appointment[]>([])
const loading = ref(true)
const errorMsg = ref('')
const filters = reactive({ from: '', to: '', status: '' })

async function load() {
  loading.value = true
  try {
    const f: Record<string, string> = {}
    if (filters.from) f.from = filters.from
    if (filters.to) f.to = filters.to
    if (filters.status) f.status = filters.status
    items.value = await useAppointments().listAll(f)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

function fmt(dt: string) {
  return new Date(dt).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Agendamentos</h1>
      <NuxtLink to="/admin/appointments/new" class="btn-primary">+ Novo</NuxtLink>
    </div>

    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 grid sm:grid-cols-4 gap-3 mb-4">
      <div><label class="field-label">De</label><input v-model="filters.from" type="date" class="input-field" /></div>
      <div><label class="field-label">Até</label><input v-model="filters.to" type="date" class="input-field" /></div>
      <div>
        <label class="field-label">Status</label>
        <select v-model="filters.status" class="input-field">
          <option value="">Todos</option>
          <option value="agendada">agendada</option>
          <option value="realizada">realizada</option>
          <option value="cancelada">cancelada</option>
          <option value="no_show">no_show</option>
        </select>
      </div>
      <button @click="load" class="btn-primary self-end">Filtrar</button>
    </div>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <table v-else class="w-full bg-white rounded-xl overflow-hidden shadow-sm">
      <thead class="bg-gray-50 text-xs uppercase text-gray-500">
        <tr><th class="text-left px-4 py-3">Data</th><th class="text-left px-4 py-3">Paciente</th><th class="text-left px-4 py-3">Médico</th><th class="px-4 py-3">Status</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="a in items" :key="a.id" class="border-t border-gray-100">
          <td class="px-4 py-3 text-sm">{{ fmt(a.scheduled_at) }}</td>
          <td class="px-4 py-3 text-sm">{{ a.patient.name }}</td>
          <td class="px-4 py-3 text-sm">{{ a.doctor.name }}</td>
          <td class="px-4 py-3 text-center text-xs">{{ a.status }}</td>
          <td class="px-4 py-3 text-right">
            <NuxtLink :to="`/appointments/${a.id}`" class="text-brand-600 hover:underline text-sm">abrir</NuxtLink>
          </td>
        </tr>
        <tr v-if="items.length === 0"><td colspan="5" class="text-center py-8 text-gray-400">Nenhum agendamento.</td></tr>
      </tbody>
    </table>
  </section>
</template>
