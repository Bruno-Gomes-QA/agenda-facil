<script setup lang="ts">
import type { DoctorPublic } from '~/types/doctor'
import type { Specialty } from '~/types/specialty'
import type { AvailabilitySlot } from '~/types/availability'

definePageMeta({ layout: 'patient', middleware: 'auth', requiredRoles: ['paciente'] })

const route = useRoute()
const router = useRouter()

const specialties = ref<Specialty[]>([])
const doctors = ref<DoctorPublic[]>([])
const specialtyId = ref<number | ''>('')
const doctorId = ref<number | ''>(route.query.doctor_id ? Number(route.query.doctor_id) : '')
const date = ref<string>(new Date().toISOString().slice(0, 10))
const slots = ref<AvailabilitySlot[]>([])
const selectedSlot = ref<string>('')
const reason = ref('')
const loadingSlots = ref(false)
const submitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

onMounted(async () => {
  try {
    specialties.value = await useSpecialties().list()
  } catch { /* ignore */ }
  await loadDoctors()
})

async function loadDoctors() {
  try {
    const filters: { specialty_id?: number } = {}
    if (specialtyId.value) filters.specialty_id = Number(specialtyId.value)
    doctors.value = await useDoctors().list(filters)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function loadSlots() {
  if (!doctorId.value || !date.value) {
    slots.value = []
    return
  }
  loadingSlots.value = true
  errorMsg.value = ''
  try {
    const res = await useAvailability().getSlots(Number(doctorId.value), date.value)
    slots.value = res.slots
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Não foi possível carregar horários.')
    slots.value = []
  } finally {
    loadingSlots.value = false
  }
}

watch(specialtyId, async () => {
  doctorId.value = ''
  slots.value = []
  await loadDoctors()
})

watch([doctorId, date], loadSlots, { immediate: true })

function fmtSlot(s: string) {
  return new Date(s).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

async function submit() {
  if (!doctorId.value || !selectedSlot.value) {
    errorMsg.value = 'Selecione um médico e um horário.'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const appt = await useAppointments().create({
      doctor_id: Number(doctorId.value),
      scheduled_at: selectedSlot.value,
      reason: reason.value || undefined,
    })
    successMsg.value = 'Consulta agendada!'
    setTimeout(() => router.push(`/appointments/${appt.id}`), 700)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Erro ao agendar consulta.')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="max-w-3xl mx-auto">
    <NuxtLink to="/appointments" class="text-sm text-brand-600 hover:underline">← Voltar</NuxtLink>
    <h1 class="text-2xl font-bold text-gray-900 mt-2 mb-6">Agendar Consulta</h1>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
      {{ errorMsg }}
    </div>
    <div v-if="successMsg" class="mb-4 bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm">
      {{ successMsg }}
    </div>

    <form @submit.prevent="submit" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
      <div>
        <label class="field-label">Especialidade (opcional)</label>
        <select v-model="specialtyId" class="input-field">
          <option value="">Todas</option>
          <option v-for="s in specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <div>
        <label class="field-label">Médico *</label>
        <select v-model="doctorId" class="input-field" required>
          <option value="">Selecione um médico</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">
            {{ d.name }} — {{ d.specialty.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="field-label">Data *</label>
        <input v-model="date" type="date" class="input-field" :min="new Date().toISOString().slice(0,10)" required />
      </div>

      <div v-if="doctorId">
        <label class="field-label">Horário *</label>
        <p v-if="loadingSlots" class="text-sm text-gray-500">Carregando horários…</p>
        <p v-else-if="slots.length === 0" class="text-sm text-gray-500">Nenhum horário disponível nesta data.</p>
        <div v-else class="grid grid-cols-4 sm:grid-cols-6 gap-2">
          <button
            v-for="s in slots"
            :key="s.datetime"
            type="button"
            :disabled="!s.available"
            @click="selectedSlot = s.datetime"
            :class="['py-2 text-sm rounded-lg border transition-colors',
              selectedSlot === s.datetime ? 'bg-brand-600 text-white border-brand-600'
              : s.available ? 'bg-white border-gray-300 hover:border-brand-400 text-gray-700'
              : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed line-through']"
          >
            {{ fmtSlot(s.datetime) }}
          </button>
        </div>
      </div>

      <div>
        <label class="field-label">Motivo (opcional)</label>
        <textarea v-model="reason" rows="3" class="input-field" placeholder="Ex.: dor de cabeça frequente" />
      </div>

      <button type="submit" :disabled="submitting" class="btn-primary w-full">
        {{ submitting ? 'Agendando…' : 'Confirmar agendamento' }}
      </button>
    </form>
  </section>
</template>
