<script setup lang="ts">
import type { Appointment } from '~/types/appointment'

definePageMeta({ layout: 'doctor', middleware: 'auth', requiredRoles: ['medico'] })

const items = ref<Appointment[]>([])
const loading = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  try {
    items.value = await useAppointments().listDoctor({})
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
})

const uniquePatients = computed(() => {
  const map = new Map<number, { id: number; name: string; email: string; count: number }>()
  for (const a of items.value) {
    const p = a.patient
    const cur = map.get(p.id)
    if (cur) cur.count += 1
    else map.set(p.id, { id: p.id, name: p.name, email: p.email, count: 1 })
  }
  return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name))
})
</script>

<template>
  <section class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Meus Pacientes</h1>
    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>
    <div v-if="loading" class="py-10 text-center text-gray-500">Carregando…</div>
    <ul v-else class="space-y-2">
      <li v-for="p in uniquePatients" :key="p.id" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center gap-4">
        <div class="w-10 h-10 rounded-full bg-teal-100 text-teal-600 flex items-center justify-center">👤</div>
        <div class="flex-1">
          <p class="font-semibold text-gray-900">{{ p.name }}</p>
          <p class="text-sm text-gray-500">{{ p.email }}</p>
        </div>
        <span class="text-xs text-gray-500">{{ p.count }} consulta(s)</span>
      </li>
      <li v-if="uniquePatients.length === 0" class="text-center py-10 text-gray-400">Nenhum paciente atendido ainda.</li>
    </ul>
  </section>
</template>
