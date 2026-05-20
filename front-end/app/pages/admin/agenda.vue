<script setup lang="ts">
import type { Appointment } from '~/types/appointment'
import type { DoctorPublic } from '~/types/doctor'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const route = useRoute()
const router = useRouter()
const today = new Date().toISOString().slice(0, 10)
const date = ref<string>((route.query.date as string) || today)
const doctorId = ref<number | ''>(route.query.doctor_id ? Number(route.query.doctor_id) : '')

const doctors = ref<DoctorPublic[]>([])
const items = ref<Appointment[]>([])
const loading = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  doctors.value = await useDoctors().list()
  await load()
})

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const f: Record<string, string | number> = { from: date.value, to: date.value }
    if (doctorId.value) f.doctor_id = Number(doctorId.value)
    items.value = await useAppointments().listAll(f as never)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}

watch([date, doctorId], () => {
  router.replace({ query: { date: date.value, ...(doctorId.value ? { doctor_id: doctorId.value } : {}) } })
  load()
})

function fmtTime(dt: string) {
  return new Date(dt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <section>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Agenda diária</h1>

    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 grid sm:grid-cols-3 gap-3 mb-4">
      <div><label class="field-label">Data</label><input v-model="date" type="date" class="input-field" /></div>
      <div>
        <label class="field-label">Médico</label>
        <select v-model="doctorId" class="input-field">
          <option value="">Todos</option>
          <option v-for="d in doctors" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
    </div>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>
    <div v-if="loading" class="text-center py-10 text-gray-500">Carregando…</div>

    <ul v-else class="space-y-2">
      <li v-for="a in items" :key="a.id" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4">
        <span class="text-lg font-mono w-16 text-gray-700">{{ fmtTime(a.scheduled_at) }}</span>
        <div class="flex-1">
          <p class="font-semibold">{{ a.patient.name }}</p>
          <p class="text-sm text-gray-500">{{ a.doctor.name }} · {{ a.doctor.specialty.name }}</p>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{{ a.status }}</span>
        <NuxtLink :to="`/appointments/${a.id}`" class="text-brand-600 text-sm hover:underline">abrir</NuxtLink>
      </li>
      <li v-if="items.length === 0" class="text-center py-10 text-gray-400">Nenhum agendamento.</li>
    </ul>
  </section>
</template>
