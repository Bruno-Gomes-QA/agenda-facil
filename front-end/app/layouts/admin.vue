<template>
  <div class="min-h-screen flex bg-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-brand-900 text-white flex flex-col shrink-0 shadow-xl">
      <div class="p-5 flex items-center gap-3 border-b border-brand-800">
        <AppLogo class="w-9 h-9 text-brand-200" />
        <div>
          <p class="text-sm font-bold leading-none text-white">Agenda Fácil</p>
          <p class="text-xs text-brand-300 mt-0.5">Recepção</p>
        </div>
      </div>

      <nav class="flex-1 px-3 py-4 space-y-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-brand-200 hover:bg-brand-800 hover:text-white"
          active-class="bg-brand-700 text-white"
        >
          <span class="text-lg">{{ item.icon }}</span>
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="p-4 border-t border-brand-800">
        <UserMenuSidebar />
      </div>
    </aside>

    <!-- Conteúdo principal -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
        <h1 class="text-base font-semibold text-gray-700">Painel Administrativo</h1>
      </header>

      <main class="flex-1 overflow-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const navItems = [
  { to: '/admin', icon: '📊', label: 'Dashboard' },
  { to: '/admin/appointments', icon: '📅', label: 'Agendamentos' },
  { to: '/admin/patients', icon: '👤', label: 'Pacientes' },
  { to: '/admin/doctors', icon: '🩺', label: 'Médicos' },
  { to: '/admin/specialties', icon: '🏷️', label: 'Especialidades' },
]
</script>
