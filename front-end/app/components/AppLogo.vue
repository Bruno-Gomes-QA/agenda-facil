<template>
  <!-- Ícone: calendário com cruz médica -->
  <svg
    viewBox="0 0 40 40"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    :class="$attrs.class"
  >
    <!-- Corpo do calendário -->
    <rect x="4" y="10" width="32" height="26" rx="4" stroke="currentColor" stroke-width="2.5" />
    <!-- Topo do calendário -->
    <path d="M4 17h32" stroke="currentColor" stroke-width="2" opacity="0.35" />
    <rect x="4" y="10" width="32" height="7" rx="4" fill="currentColor" fill-opacity="0.15" />
    <!-- Ganchos -->
    <line x1="13" y1="5" x2="13" y2="14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
    <line x1="27" y1="5" x2="27" y2="14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
    <!-- Cruz médica -->
    <line x1="20" y1="23" x2="20" y2="31" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
    <line x1="16" y1="27" x2="24" y2="27" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
  </svg>
</template>
