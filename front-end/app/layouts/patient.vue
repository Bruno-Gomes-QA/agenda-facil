<template>
  <div class="min-h-screen bg-blue-50 flex flex-col">
    <!-- Header paciente -->
    <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-2.5">
        <AppLogo class="w-8 h-8 text-brand-600" />
        <span class="text-lg font-bold tracking-tight text-gray-900">Agenda Fácil</span>
      </div>

      <nav class="flex items-center gap-6 text-sm font-medium">
        <NuxtLink to="/appointments" class="text-gray-600 hover:text-brand-600 transition-colors">
          Meus Agendamentos
        </NuxtLink>
        <NuxtLink to="/appointments/new" class="btn-primary text-sm py-1.5 px-4">
          Agendar Consulta
        </NuxtLink>
        <UserMenu />
      </nav>
    </header>

    <main class="flex-1 p-6">
      <slot />
    </main>
  </div>
</template>
