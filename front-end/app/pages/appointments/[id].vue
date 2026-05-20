<script setup lang="ts">
import type { Appointment } from '~/types/appointment'
import type { AvailabilitySlot } from '~/types/availability'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)
const auth = useAuthStore()

const layout = computed(() => {
  if (auth.user?.role === 'medico') return 'doctor'
  if (auth.user?.role === 'recepcionista') return 'admin'
  return 'patient'
})

const appt = ref<Appointment | null>(null)
const loading = ref(true)
const errorMsg = ref('')
const actionMsg = ref('')

const showReschedule = ref(false)
const rescheduleDate = ref(new Date().toISOString().slice(0, 10))
const rescheduleSlots = ref<AvailabilitySlot[]>([])
const rescheduleSelected = ref('')
const loadingRescheduleSlots = ref(false)

async function load() {
  loading.value = true
  try {
    appt.value = await useAppointments().get(id)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Agendamento não encontrado.')
  } finally {
    loading.value = false
  }
}

onMounted(load)

watch([showReschedule, rescheduleDate], async () => {
  if (!showReschedule.value || !appt.value) return
  loadingRescheduleSlots.value = true
  try {
    const res = await useAvailability().getSlots(appt.value.doctor.id, rescheduleDate.value)
    rescheduleSlots.value = res.slots
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loadingRescheduleSlots.value = false
  }
})

async function doReschedule() {
  if (!appt.value || !rescheduleSelected.value) return
  try {
    appt.value = await useAppointments().reschedule(appt.value.id, rescheduleSelected.value)
    actionMsg.value = 'Consulta remarcada.'
    showReschedule.value = false
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Não foi possível remarcar.')
  }
}

async function doCancel() {
  if (!appt.value) return
  if (!confirm('Deseja realmente cancelar esta consulta?')) return
  try {
    appt.value = await useAppointments().cancel(appt.value.id)
    actionMsg.value = 'Consulta cancelada.'
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Não foi possível cancelar.')
  }
}

function fmt(dt: string) {
  return new Date(dt).toLocaleString('pt-BR', { dateStyle: 'long', timeStyle: 'short' })
}
function fmtSlot(s: string) {
  return new Date(s).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const canModify = computed(() => appt.value?.status === 'agendada')
</script>

<template>
  <NuxtLayout :name="layout">
    <section class="max-w-3xl mx-auto">
      <button @click="router.back()" class="text-sm text-brand-600 hover:underline">← Voltar</button>

      <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
      <div v-else-if="errorMsg && !appt" class="text-center py-12 text-red-600">{{ errorMsg }}</div>

      <article v-else-if="appt" class="mt-4 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h1 class="text-xl font-bold text-gray-900">Consulta #{{ appt.id }}</h1>
            <p class="text-gray-500 text-sm">Criada em {{ fmt(appt.created_at) }}</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">
            {{ appt.status }}
          </span>
        </div>

        <div v-if="actionMsg" class="mt-4 bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm">
          {{ actionMsg }}
        </div>
        <div v-if="errorMsg" class="mt-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
          {{ errorMsg }}
        </div>

        <dl class="mt-6 grid sm:grid-cols-2 gap-y-3 gap-x-6 text-sm">
          <div>
            <dt class="text-gray-500">Médico</dt>
            <dd class="font-medium text-gray-900">{{ appt.doctor.name }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Especialidade</dt>
            <dd class="font-medium text-gray-900">{{ appt.doctor.specialty.name }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Paciente</dt>
            <dd class="font-medium text-gray-900">{{ appt.patient.name }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Data e hora</dt>
            <dd class="font-medium text-gray-900">{{ fmt(appt.scheduled_at) }}</dd>
          </div>
          <div class="sm:col-span-2">
            <dt class="text-gray-500">Motivo</dt>
            <dd class="text-gray-900">{{ appt.reason || '—' }}</dd>
          </div>
          <div v-if="appt.doctor_notes !== null" class="sm:col-span-2">
            <dt class="text-gray-500">Anotações do médico</dt>
            <dd class="text-gray-900 whitespace-pre-line">{{ appt.doctor_notes || '—' }}</dd>
          </div>
        </dl>

        <div v-if="canModify" class="mt-6 flex flex-wrap gap-3">
          <button @click="showReschedule = !showReschedule" class="btn-primary">
            {{ showReschedule ? 'Cancelar remarcação' : 'Remarcar' }}
          </button>
          <button
            @click="doCancel"
            class="px-4 py-2 rounded-lg bg-red-50 text-red-700 border border-red-200 font-medium hover:bg-red-100 text-sm"
          >
            Cancelar consulta
          </button>
        </div>

        <div v-if="showReschedule" class="mt-6 border-t pt-6">
          <h3 class="font-semibold text-gray-900 mb-3">Escolher novo horário</h3>
          <input v-model="rescheduleDate" type="date" class="input-field mb-3" :min="new Date().toISOString().slice(0,10)" />
          <p v-if="loadingRescheduleSlots" class="text-sm text-gray-500">Carregando…</p>
          <div v-else class="grid grid-cols-4 sm:grid-cols-6 gap-2">
            <button
              v-for="s in rescheduleSlots"
              :key="s.datetime"
              type="button"
              :disabled="!s.available"
              @click="rescheduleSelected = s.datetime"
              :class="['py-2 text-sm rounded-lg border transition-colors',
                rescheduleSelected === s.datetime ? 'bg-brand-600 text-white border-brand-600'
                : s.available ? 'bg-white border-gray-300 hover:border-brand-400 text-gray-700'
                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed line-through']"
            >
              {{ fmtSlot(s.datetime) }}
            </button>
          </div>
          <button @click="doReschedule" :disabled="!rescheduleSelected" class="btn-primary mt-4">
            Confirmar nova data
          </button>
        </div>
      </article>
    </section>
  </NuxtLayout>
</template>
