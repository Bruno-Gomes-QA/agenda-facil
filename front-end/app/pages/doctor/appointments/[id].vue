<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'doctor', middleware: 'auth', requiredRoles: ['medico'] })

const route = useRoute()
const id = Number(route.params.id)
const appt = ref<Appointment | null>(null)
const loading = ref(true)
const errorMsg = ref('')
const actionMsg = ref('')
const notes = ref('')

async function load() {
  loading.value = true
  try {
    appt.value = await useAppointments().get(id)
    notes.value = appt.value.doctor_notes ?? ''
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function setStatus(status: 'realizada' | 'no_show') {
  if (!appt.value) return
  try {
    appt.value = await useAppointments().setStatus(appt.value.id, status)
    actionMsg.value = `Status alterado para ${status}.`
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function saveNotes() {
  if (!appt.value) return
  try {
    appt.value = await useAppointments().setNotes(appt.value.id, notes.value)
    actionMsg.value = 'Anotações salvas.'
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

function fmt(dt: string) {
  return new Date(dt).toLocaleString('pt-BR', { dateStyle: 'long', timeStyle: 'short' })
}
</script>

<template>
  <section class="max-w-3xl mx-auto">
    <NuxtLink to="/doctor/agenda" class="text-sm text-teal-600 hover:underline">← Voltar</NuxtLink>

    <div v-if="loading" class="py-10 text-center text-gray-500">Carregando…</div>
    <div v-else-if="!appt" class="py-10 text-red-600">{{ errorMsg || 'Consulta não encontrada.' }}</div>

    <article v-else class="mt-4 bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-xl font-bold text-gray-900">{{ appt.patient.name }}</h1>
          <p class="text-gray-500 text-sm">{{ fmt(appt.scheduled_at) }}</p>
        </div>
        <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">{{ appt.status }}</span>
      </div>

      <div v-if="actionMsg" class="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm">{{ actionMsg }}</div>
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

      <div>
        <p class="text-gray-500 text-sm">Motivo informado</p>
        <p class="text-gray-900">{{ appt.reason || '—' }}</p>
      </div>

      <div>
        <label class="field-label">Anotações clínicas (privadas)</label>
        <textarea v-model="notes" rows="6" class="input-field" />
        <button @click="saveNotes" class="btn-primary mt-2">Salvar anotações</button>
      </div>

      <div class="flex gap-3 pt-2 border-t">
        <button @click="setStatus('realizada')" class="btn-primary">Marcar como realizada</button>
        <button @click="setStatus('no_show')" class="px-4 py-2 rounded-lg bg-orange-50 text-orange-700 border border-orange-200 font-medium hover:bg-orange-100 text-sm">
          Marcar no-show
        </button>
      </div>
    </article>
  </section>
</template>
