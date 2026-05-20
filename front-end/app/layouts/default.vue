<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <NuxtLink to="/" class="flex items-center gap-2.5 text-brand-600 hover:text-brand-700 transition-colors">
        <AppLogo class="w-8 h-8" />
        <span class="text-lg font-bold tracking-tight text-gray-900">Agenda Fácil</span>
      </NuxtLink>

      <nav class="flex items-center gap-4">
        <NuxtLink to="/login" class="text-sm text-gray-500 hover:text-brand-600 transition-colors font-medium">
          Entrar
        </NuxtLink>
        <NuxtLink to="/register" class="btn-primary text-sm py-1.5 px-4">
          Criar conta
        </NuxtLink>
      </nav>
    </header>

    <!-- Conteúdo -->
    <main class="flex-1">
      <slot />
    </main>

    <footer class="text-center text-xs text-gray-400 py-4">
      © {{ new Date().getFullYear() }} Agenda Fácil — BUGBUSTERS
    </footer>
  </div>
</template>
