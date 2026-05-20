<template>
  <div class="min-h-screen bg-teal-50 flex flex-col">
    <header class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div class="flex items-center gap-2.5">
        <AppLogo class="w-8 h-8 text-teal-600" />
        <div>
          <p class="text-sm font-bold text-gray-900 leading-none">Agenda Fácil</p>
          <p class="text-xs text-teal-600 font-medium mt-0.5">Área do Médico</p>
        </div>
      </div>

      <nav class="flex items-center gap-6 text-sm font-medium">
        <NuxtLink to="/doctor/agenda" class="text-gray-600 hover:text-teal-600 transition-colors">
          Minha Agenda
        </NuxtLink>
        <NuxtLink to="/doctor/patients" class="text-gray-600 hover:text-teal-600 transition-colors">
          Pacientes
        </NuxtLink>
        <UserMenu />
      </nav>
    </header>

    <main class="flex-1 p-6">
      <slot />
    </main>
  </div>
</template>
