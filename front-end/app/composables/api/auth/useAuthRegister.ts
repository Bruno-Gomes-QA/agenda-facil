import type { PatientCreate, UserOut } from '~/types/auth'

/**
 * Cadastro de paciente + auto-login após o registro.
 */
export function useAuthRegister() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  async function register(data: PatientCreate): Promise<UserOut> {
    const baseURL = config.public.apiBaseUrl as string

    // 1. Cria o paciente
    const user = await $fetch<UserOut>('/users', {
      baseURL,
      method: 'POST',
      body: data,
    })

    // 2. Auto-login: obtém token diretamente
    const loginRes = await $fetch('/auth/login', {
      baseURL,
      method: 'POST',
      body: { email: data.email, password: data.password },
    }) as { access_token: string; user: UserOut }

    auth.setAuth(loginRes.access_token, loginRes.user)

    return user
  }

  return { register }
}
