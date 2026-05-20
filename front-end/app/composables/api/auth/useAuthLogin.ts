import type { LoginResponse } from '~/types/auth'

/**
 * Login — usa $fetch (não useFetch) pois é uma ação imperativa, não reativa.
 */
export function useAuthLogin() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  async function login(email: string, password: string): Promise<LoginResponse> {
    const data = await $fetch<LoginResponse>('/auth/login', {
      baseURL: config.public.apiBaseUrl as string,
      method: 'POST',
      body: { email, password },
    })
    auth.setAuth(data.access_token, data.user)
    return data
  }

  return { login }
}
