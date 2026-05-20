<template>
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-2.5 min-w-0">
      <span
        class="w-8 h-8 rounded-full bg-brand-700 text-white font-bold text-xs flex items-center justify-center uppercase shrink-0"
      >
        {{ initials }}
      </span>
      <div class="min-w-0">
        <p class="text-sm font-medium text-white truncate">{{ auth.user?.name?.split(' ')[0] }}</p>
        <p class="text-xs text-brand-300 truncate">{{ auth.user?.role }}</p>
      </div>
    </div>
    <button
      @click="handleLogout"
      title="Sair"
      class="ml-2 text-brand-400 hover:text-white transition-colors"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { initials as getInitials } from '~/lib/format'

const auth = useAuthStore()
const initials = computed(() => getInitials(auth.user?.name ?? ''))

function handleLogout() {
  auth.logout()
  navigateTo('/login')
}
</script>
