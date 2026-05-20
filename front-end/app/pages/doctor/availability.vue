<script setup lang="ts">
import type { AvailabilityRule } from '~/types/availability'

definePageMeta({ layout: 'doctor', middleware: 'auth', requiredRoles: ['medico'] })

const meId = ref<number | null>(null)
const rules = ref<AvailabilityRule[]>([])
const loading = ref(true)
const errorMsg = ref('')
const newRule = reactive({ weekday: 1, start_time: '08:00', end_time: '12:00' })
const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

async function load() {
  loading.value = true
  try {
    if (!meId.value) {
      const me = await useDoctors().getMe()
      meId.value = me.id
    }
    if (meId.value) {
      rules.value = await useAvailability().listRules(meId.value)
    }
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function addRule() {
  if (!meId.value) return
  try {
    await useAvailability().createRule(meId.value, { ...newRule })
    rules.value = await useAvailability().listRules(meId.value)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}

async function remove(id: number) {
  if (!meId.value) return
  if (!confirm('Remover esta regra?')) return
  try {
    await useAvailability().deleteRule(meId.value, id)
    rules.value = await useAvailability().listRules(meId.value)
  } catch (err) {
    errorMsg.value = apiErrorMessage(err)
  }
}
</script>

<template>
  <section class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Minha disponibilidade</h1>

    <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">{{ errorMsg }}</div>
    <div v-if="loading" class="py-10 text-center text-gray-500">Carregando…</div>

    <div v-else>
      <ul class="space-y-2 mb-6">
        <li v-for="r in rules" :key="r.id" class="bg-white rounded-xl p-3 shadow-sm border border-gray-100 flex items-center gap-3">
          <span class="font-medium w-12">{{ weekdays[r.weekday] }}</span>
          <span class="text-gray-700">{{ r.start_time.slice(0,5) }} – {{ r.end_time.slice(0,5) }}</span>
          <button @click="remove(r.id)" class="ml-auto text-red-500 hover:text-red-700 text-sm">remover</button>
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
