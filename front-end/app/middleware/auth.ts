/**
 * middleware/auth.ts — middleware nomeado para proteger rotas autenticadas.
 *
 * Uso: definePageMeta({ middleware: 'auth' })
 * Com roles: definePageMeta({ middleware: 'auth', requiredRoles: ['recepcionista'] })
 */
import type { UserRole } from '~/types/auth'

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  const required = (to.meta.requiredRoles as UserRole[] | undefined) ?? []
  if (required.length > 0) {
    const role = auth.user?.role
    if (!role || !required.includes(role)) {
      return navigateTo(auth.dashboardRoute())
    }
  }
})
