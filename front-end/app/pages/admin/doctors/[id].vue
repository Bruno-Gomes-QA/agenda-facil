<script setup lang="ts">
import type { Doctor } from '~/types/doctor'
import type { AvailabilityRule } from '~/types/availability'

definePageMeta({ layout: 'admin', middleware: 'auth', requiredRoles: ['recepcionista'] })

const route = useRoute()
const id = Number(route.params.id)
const doctor = ref<Doctor | null>(null)
const rules = ref<AvailabilityRule[]>([])
const loading = ref(true)
const errorMsg = ref('')

const newRule = reactive({ weekday: 1, start_time: '08:00', end_time: '12:00' })

const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

async function load() {
  loading.value = true
  try {
    doctor.value = await useDoctors().getFull(id)
    rules.value = await useAvailability().listRules(id)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function addRule() {
  try {
    await useAvailability().createRule(id, {
      weekday: newRule.weekday,
      start_time: newRule.start_time,
      end_time: newRule.end_time,
    })
    rules.value = await useAvailability().listRules(id)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function removeRule(ruleId: number) {
  if (!confirm('Remover esta regra de disponibilidade?')) return
  try {
    await useAvailability().deleteRule(id, ruleId)
    rules.value = await useAvailability().listRules(id)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}
</script>

<template>
  <section class="max-w-3xl">
    <NuxtLink to="/admin/doctors" class="text-sm text-brand-600 hover:underline">← Voltar</NuxtLink>

    <div v-if="loading" class="py-10 text-center text-gray-500">Carregando…</div>
    <div v-else-if="!doctor" class="py-10 text-red-600">{{ errorMsg || 'Médico não encontrado.' }}</div>

    <div v-else>
      <h1 class="text-2xl font-bold text-gray-900 mt-2">{{ doctor.name }}</h1>
      <p class="text-gray-500 mb-6">{{ doctor.specialty.name }} · CRM {{ doctor.crm }}</p>

      <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>

      <h2 class="text-lg font-semibold text-gray-900 mb-3">Regras de disponibilidade</h2>
      <ul class="space-y-2 mb-6">
        <li v-for="r in rules" :key="r.id" class="bg-white rounded-xl p-3 shadow-sm border border-gray-100 flex items-center gap-3">
          <span class="font-medium w-12">{{ weekdays[r.weekday] }}</span>
          <span class="text-gray-700">{{ r.start_time.slice(0,5) }} – {{ r.end_time.slice(0,5) }}</span>
          <button @click="removeRule(r.id)" class="ml-auto text-red-500 hover:text-red-700 text-sm">remover</button>
        </li>
        <li v-if="rules.length === 0" class="text-center py-4 text-gray-400 text-sm">Nenhuma regra cadastrada.</li>
      </ul>

      <form @submit.prevent="addRule" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 grid sm:grid-cols-4 gap-3 items-end">
        <div>
          <label class="field-label">Dia</label>
          <select v-model.number="newRule.weekday" class="input-field">
            <option v-for="(w, i) in weekdays" :key="i" :value="i">{{ w }}</option>
          </select>
        </div>
        <div>
          <label class="field-label">Início</label>
          <input v-model="newRule.start_time" type="time" class="input-field" required />
        </div>
        <div>
          <label class="field-label">Fim</label>
          <input v-model="newRule.end_time" type="time" class="input-field" required />
        </div>
        <button type="submit" class="btn-primary">Adicionar</button>
      </form>
    </div>
  </section>
</template>
