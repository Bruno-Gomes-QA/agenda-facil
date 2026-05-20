<script setup lang="ts">
definePageMeta({ layout: false })

const auth = useAuthStore()

// Redireciona para o dashboard do papel correto ou para login
onMounted(() => {
  if (auth.isAuthenticated) {
    navigateTo(auth.dashboardRoute())
  } else {
    navigateTo('/login')
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="animate-spin w-8 h-8 border-4 border-brand-600 border-t-transparent rounded-full" />
  </div>
</template>
