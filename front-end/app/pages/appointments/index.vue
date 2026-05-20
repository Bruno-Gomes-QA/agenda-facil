<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'patient', middleware: 'auth', requiredRoles: ['paciente'] })

const tab = ref<'proximas' | 'historico'>('proximas')
const loading = ref(true)
const errorMsg = ref('')
const appointments = ref<Appointment[]>([])

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    appointments.value = await useAppointments().listMine()
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Não foi possível carregar seus agendamentos.')
  } finally {
    loading.value = false
  }
}

onMounted(load)

const now = new Date()
const proximas = computed(() =>
  appointments.value
    .filter(a => a.status === 'agendada' && new Date(a.scheduled_at) >= now)
    .sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at)),
)
const historico = computed(() =>
  appointments.value
    .filter(a => a.status !== 'agendada' || new Date(a.scheduled_at) < now)
    .sort((a, b) => b.scheduled_at.localeCompare(a.scheduled_at)),
)

function fmt(dt: string) {
  return new Date(dt).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function statusBadge(s: string) {
  const map: Record<string, string> = {
    agendada: 'bg-blue-100 text-blue-700',
    realizada: 'bg-green-100 text-green-700',
    cancelada: 'bg-red-100 text-red-700',
    no_show: 'bg-orange-100 text-orange-700',
  }
  return map[s] || 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <section class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Meus Agendamentos</h1>
      <NuxtLink to="/appointments/new" class="btn-primary">+ Nova consulta</NuxtLink>
    </div>

    <div class="flex gap-1 mb-4 border-b border-gray-200">
      <button
        @click="tab = 'proximas'"
        :class="['px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
          tab === 'proximas' ? 'border-brand-600 text-brand-700' : 'border-transparent text-gray-500 hover:text-gray-700']"
      >
        Próximas ({{ proximas.length }})
      </button>
      <button
        @click="tab = 'historico'"
        :class="['px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
          tab === 'historico' ? 'border-brand-600 text-brand-700' : 'border-transparent text-gray-500 hover:text-gray-700']"
      >
        Histórico ({{ historico.length }})
      </button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <div v-else-if="errorMsg" class="text-center py-12 text-red-600">{{ errorMsg }}</div>

    <ul v-else class="space-y-3">
      <li
        v-for="a in (tab === 'proximas' ? proximas : historico)"
        :key="a.id"
        class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 shrink-0">📅</div>
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-gray-900">{{ a.doctor.name }}</p>
          <p class="text-sm text-gray-500">{{ a.doctor.specialty.name }} · {{ fmt(a.scheduled_at) }}</p>
        </div>
        <span :class="['text-xs font-semibold px-2.5 py-1 rounded-full', statusBadge(a.status)]">
          {{ a.status }}
        </span>
        <NuxtLink :to="`/appointments/${a.id}`" class="text-sm text-brand-600 hover:underline">Detalhes →</NuxtLink>
      </li>
      <li v-if="(tab === 'proximas' ? proximas : historico).length === 0" class="text-center py-12 text-gray-400">
        Nada por aqui.
      </li>
    </ul>
  </section>
</template>
