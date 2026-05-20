<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'doctor', middleware: 'auth', requiredRoles: ['medico'] })

const date = ref(new Date().toISOString().slice(0, 10))
const items = ref<Appointment[]>([])
const loading = ref(true)
const errorMsg = ref('')

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    items.value = await useAppointments().listDoctor({ date: date.value })
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)
watch(date, load)

function fmtTime(dt: string) {
  return new Date(dt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <section class="max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Minha Agenda</h1>

    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-4 max-w-xs">
      <label class="field-label">Data</label>
      <input v-model="date" type="date" class="input-field" />
    </div>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>
    <div v-if="loading" class="text-center py-10 text-gray-500">Carregando…</div>

    <ul v-else class="space-y-2">
      <li v-for="a in items" :key="a.id" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4">
        <span class="text-lg font-mono w-16 text-gray-700">{{ fmtTime(a.scheduled_at) }}</span>
        <div class="flex-1">
          <p class="font-semibold">{{ a.patient.name }}</p>
          <p class="text-sm text-gray-500">{{ a.reason || 'Sem motivo informado' }}</p>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{{ a.status }}</span>
        <NuxtLink :to="`/doctor/appointments/${a.id}`" class="text-teal-600 text-sm hover:underline">atender</NuxtLink>
      </li>
      <li v-if="items.length === 0" class="text-center py-10 text-gray-400">Nada agendado para esta data.</li>
    </ul>

    <p class="mt-6 text-sm text-gray-500">
      Quer ajustar seus horários? <NuxtLink to="/doctor/availability" class="text-teal-600 hover:underline">Editar disponibilidade</NuxtLink>
    </p>
  </section>
</template>
