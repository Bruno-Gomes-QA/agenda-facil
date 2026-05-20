<script setup lang="ts">
import type { DoctorPublic } from '~/types/doctor'
import type { UserOut } from '~/types/auth'
import type { AvailabilitySlot } from '~/types/availability'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const router = useRouter()
const doctors = ref<DoctorPublic[]>([])
const patients = ref<UserOut[]>([])
const doctorId = ref<number | ''>('')
const patientId = ref<number | ''>('')
const date = ref(new Date().toISOString().slice(0, 10))
const slots = ref<AvailabilitySlot[]>([])
const selected = ref('')
const reason = ref('')
const errorMsg = ref('')
const submitting = ref(false)

onMounted(async () => {
  try {
    [doctors.value, patients.value] = await Promise.all([
      useDoctors().list(),
      useAdminPatients().list(),
    ])
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
})

watch([doctorId, date], async () => {
  selected.value = ''
  if (!doctorId.value) { slots.value = []; return }
  try {
    const res = await useAvailability().getSlots(Number(doctorId.value), date.value)
    slots.value = res.slots
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
})

function fmtSlot(s: string) {
  return new Date(s).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

async function submit() {
  if (!doctorId.value || !patientId.value || !selected.value) {
    errorMsg.value = 'Preencha todos os campos obrigatórios.'
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    const appt = await useAppointments().create({
      doctor_id: Number(doctorId.value),
      patient_id: Number(patientId.value),
      scheduled_at: selected.value,
      reason: reason.value || undefined,
    })
    router.push(`/appointments/${appt.id}`)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="max-w-3xl">
    <NuxtLink to="/admin/appointments" class="text-sm text-brand-600 hover:underline">← Voltar</NuxtLink>
    <h1 class="text-2xl font-bold text-gray-900 mt-2 mb-6">Novo agendamento</h1>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

    <form @submit.prevent="submit" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-4">
      <div>
        <label class="field-label">Paciente</label>
        <select v-model="patientId" class="input-field" required>
          <option value="">Selecione</option>
          <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.name }} ({{ p.email }})</option>
        </select>
      </div>
      <div>
        <label class="field-label">Médico</label>
        <select v-model="doctorId" class="input-field" required>
          <option value="">Selecione</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">{{ d.name }} — {{ d.specialty.name }}</option>
        </select>
      </div>
      <div>
        <label class="field-label">Data</label>
        <input v-model="date" type="date" class="input-field" required />
      </div>
      <div v-if="doctorId">
        <label class="field-label">Horário</label>
        <p v-if="slots.length === 0" class="text-sm text-gray-500">Nenhum horário disponível.</p>
        <div v-else class="grid grid-cols-4 sm:grid-cols-6 gap-2">
          <button
            v-for="s in slots"
            :key="s.datetime"
            type="button"
            :disabled="!s.available"
            @click="selected = s.datetime"
            :class="['py-2 text-sm rounded-lg border',
              selected === s.datetime ? 'bg-brand-600 text-white border-brand-600'
              : s.available ? 'bg-white border-gray-300 hover:border-brand-400 text-gray-700'
              : 'bg-gray-100 text-gray-400 border-gray-200 line-through']"
          >{{ fmtSlot(s.datetime) }}</button>
        </div>
      </div>
      <div>
        <label class="field-label">Motivo</label>
        <textarea v-model="reason" rows="3" class="input-field" />
      </div>
      <button type="submit" :disabled="submitting" class="btn-primary w-full">
        {{ submitting ? 'Salvando…' : 'Confirmar' }}
      </button>
    </form>
  </section>
</template>
