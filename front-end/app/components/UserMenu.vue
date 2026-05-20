<template>
  <div class="relative" ref="menuRef">
    <button
      @click="open = !open"
      class="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-brand-600 transition-colors"
    >
      <span
        class="w-8 h-8 rounded-full bg-brand-100 text-brand-700 font-bold text-xs flex items-center justify-center uppercase"
      >
        {{ initials }}
      </span>
      <span class="hidden md:block">{{ auth.user?.name?.split(' ')[0] }}</span>
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition name="slide-down">
      <div
        v-if="open"
        class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50"
      >
        <div class="px-4 py-2 border-b border-gray-100">
          <p class="text-xs font-medium text-gray-900 truncate">{{ auth.user?.name }}</p>
          <p class="text-xs text-gray-400 truncate">{{ auth.user?.email }}</p>
        </div>
        <button
          @click="handleLogout"
          class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
        >
          Sair
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { initials as getInitials } from '~/lib/format'

const auth = useAuthStore()
const open = ref(false)
const menuRef = ref<HTMLElement | null>(null)

const initials = computed(() => getInitials(auth.user?.name ?? ''))

onClickOutside(menuRef, () => { open.value = false })

function handleLogout() {
  auth.logout()
  navigateTo('/login')
}
</script>
