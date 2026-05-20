import { defineStore } from 'pinia'
import type { UserOut, UserRole } from '~/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const user = ref<UserOut | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  /** Auto-hidratação na primeira execução client-side */
  if (import.meta.client) {
    const storedToken = sessionStorage.getItem('auth_token')
    const storedUser = sessionStorage.getItem('auth_user')
    if (storedToken && storedUser) {
      try {
        accessToken.value = storedToken
        user.value = JSON.parse(storedUser) as UserOut
      } catch {
        sessionStorage.removeItem('auth_token')
        sessionStorage.removeItem('auth_user')
      }
    }
  }

  function setAuth(token: string, userData: UserOut) {
    accessToken.value = token
    user.value = userData
    if (import.meta.client) {
      sessionStorage.setItem('auth_token', token)
      sessionStorage.setItem('auth_user', JSON.stringify(userData))
    }
  }

  function logout() {
    accessToken.value = null
    user.value = null
    if (import.meta.client) {
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_user')
    }
  }

  /** Rota de destino pós-login por papel */
  function dashboardRoute(): string {
    const role = user.value?.role as UserRole | undefined
    if (role === 'recepcionista') return '/admin'
    if (role === 'medico') return '/doctor/agenda'
    return '/appointments'
  }

  return { accessToken, user, isAuthenticated, setAuth, logout, dashboardRoute }
})
