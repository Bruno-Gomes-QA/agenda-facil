<script setup lang="ts">
import type { DoctorPublic } from '~/types/doctor'

const route = useRoute()
const id = Number(route.params.id)
const doctor = ref<DoctorPublic | null>(null)
const loading = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  try {
    doctor.value = await useDoctors().get(id)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Médico não encontrado.')
  } finally {
    loading.value = false
  }
})

const auth = useAuthStore()
function goSchedule() {
  if (!auth.isAuthenticated) {
    navigateTo(`/login?redirect=/appointments/new?doctor_id=${id}`)
  } else {
    navigateTo(`/appointments/new?doctor_id=${id}`)
  }
}
</script>

<template>
  <section class="max-w-3xl mx-auto px-4 py-10">
    <NuxtLink to="/doctors" class="text-sm text-brand-600 hover:underline">← Voltar</NuxtLink>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <div v-else-if="errorMsg" class="text-center py-12 text-red-600">{{ errorMsg }}</div>

    <article v-else-if="doctor" class="mt-4 bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
      <div class="flex items-start gap-4">
        <div class="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-2xl shrink-0">
          🩺
        </div>
        <div class="flex-1">
          <h1 class="text-2xl font-bold text-gray-900">{{ doctor.name }}</h1>
          <p class="text-brand-600 font-medium">{{ doctor.specialty.name }}</p>
          <p class="text-xs text-gray-400">CRM {{ doctor.crm }}</p>
        </div>
      </div>

      <div v-if="doctor.bio" class="mt-6">
        <h2 class="font-semibold text-gray-700 mb-2">Sobre</h2>
        <p class="text-gray-600 whitespace-pre-line">{{ doctor.bio }}</p>
      </div>

      <button @click="goSchedule" class="btn-primary mt-8 w-full sm:w-auto">
        Agendar consulta
      </button>
    </article>
  </section>
</template>
