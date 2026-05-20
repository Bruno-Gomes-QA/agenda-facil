<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const auth = useAuthStore()
const today = new Date().toISOString().slice(0, 10)
const appointments = ref<Appointment[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    appointments.value = await useAppointments().listAll({ from: today, to: today })
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
})

const counts = computed(() => ({
  total: appointments.value.length,
  agendadas: appointments.value.filter(a => a.status === 'agendada').length,
  realizadas: appointments.value.filter(a => a.status === 'realizada').length,
  canceladas: appointments.value.filter(a => a.status === 'cancelada').length,
}))

const cards = [
  { to: '/admin/appointments', label: 'Agendamentos', icon: '📅', color: 'bg-blue-100 text-blue-700' },
  { to: '/admin/agenda', label: 'Agenda diária', icon: '🗓️', color: 'bg-purple-100 text-purple-700' },
  { to: '/admin/patients', label: 'Pacientes', icon: '👤', color: 'bg-green-100 text-green-700' },
  { to: '/admin/doctors', label: 'Médicos', icon: '🩺', color: 'bg-teal-100 text-teal-700' },
  { to: '/admin/specialties', label: 'Especialidades', icon: '🏷️', color: 'bg-amber-100 text-amber-700' },
]
</script>

<template>
  <section>
    <h1 class="text-2xl font-bold text-gray-900 mb-1">Olá, {{ auth.user?.name }}</h1>
    <p class="text-gray-500 mb-6">Visão geral da recepção.</p>

    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500">Hoje</p>
        <p class="text-2xl font-bold text-gray-900">{{ loading ? '…' : counts.total }}</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500">Agendadas</p>
        <p class="text-2xl font-bold text-blue-600">{{ loading ? '…' : counts.agendadas }}</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500">Realizadas</p>
        <p class="text-2xl font-bold text-green-600">{{ loading ? '…' : counts.realizadas }}</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500">Canceladas</p>
        <p class="text-2xl font-bold text-red-600">{{ loading ? '…' : counts.canceladas }}</p>
      </div>
    </div>

    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <NuxtLink
        v-for="c in cards"
        :key="c.to"
        :to="c.to"
        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-brand-400 hover:shadow-md transition-all flex items-center gap-4"
      >
        <div :class="['w-12 h-12 rounded-full flex items-center justify-center text-xl', c.color]">{{ c.icon }}</div>
        <span class="font-semibold text-gray-900">{{ c.label }}</span>
      </NuxtLink>
    </div>
  </section>
</template>
