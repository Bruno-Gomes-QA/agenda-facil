<script setup lang="ts">
import type { DoctorPublic } from '~/types/doctor'
import type { Specialty } from '~/types/specialty'

const search = ref('')
const specialtyFilter = ref<number | ''>('')
const loading = ref(true)
const doctors = ref<DoctorPublic[]>([])
const specialties = ref<Specialty[]>([])
const errorMsg = ref('')

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const api = useDoctors()
    const filters: { specialty_id?: number; search?: string } = {}
    if (specialtyFilter.value) filters.specialty_id = Number(specialtyFilter.value)
    if (search.value.trim()) filters.search = search.value.trim()
    doctors.value = await api.list(filters)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err, 'Não foi possível carregar os médicos.')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    specialties.value = await useSpecialties().list()
  } catch {
    /* ignora — filtro fica vazio */
  }
  await load()
})

watch([search, specialtyFilter], () => load())
</script>

<template>
  <section class="max-w-5xl mx-auto px-4 py-10">
    <h1 class="text-2xl font-bold text-gray-900 mb-2">Nossos Médicos</h1>
    <p class="text-gray-600 mb-6">Encontre o profissional ideal para sua consulta.</p>

    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <input v-model="search" type="text" placeholder="Buscar por nome…" class="input-field flex-1" />
      <select v-model="specialtyFilter" class="input-field sm:w-64">
        <option value="">Todas as especialidades</option>
        <option v-for="s in specialties" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Carregando…</div>
    <div v-else-if="errorMsg" class="text-center py-12 text-red-600">{{ errorMsg }}</div>
    <div v-else-if="doctors.length === 0" class="text-center py-12 text-gray-500">Nenhum médico encontrado.</div>

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <NuxtLink
        v-for="d in doctors"
        :key="d.id"
        :to="`/doctors/${d.id}`"
        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-brand-400 hover:shadow-md transition-all"
      >
        <div class="flex items-start gap-3">
          <div class="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-lg shrink-0">
            🩺
          </div>
          <div class="min-w-0">
            <h3 class="font-semibold text-gray-900 truncate">{{ d.name }}</h3>
            <p class="text-sm text-brand-600">{{ d.specialty.name }}</p>
            <p class="text-xs text-gray-400 mt-1">CRM {{ d.crm }}</p>
          </div>
        </div>
        <p v-if="d.bio" class="text-sm text-gray-600 mt-3 line-clamp-2">{{ d.bio }}</p>
      </NuxtLink>
    </div>
  </section>
</template>
