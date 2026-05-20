import type { UserOut } from '~/types/auth'

/**
 * Busca o perfil do usuário autenticado.
 * Útil para refrescar dados após mudança de perfil.
 */
export function useAuthMe() {
  const auth = useAuthStore()

  const { data, pending, error, refresh } = useApiFetch<UserOut>('/auth/me', {
    immediate: false,
    watch: false,
  })

  async function fetchMe() {
    await refresh()
    if (data.value) {
      // Atualiza o user no store sem alterar o token
      const token = auth.accessToken
      if (token) auth.setAuth(token, data.value)
    }
  }

  return { data, pending, error, fetchMe }
}
