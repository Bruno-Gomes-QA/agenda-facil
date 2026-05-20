/**
 * useApi — wrapper imperativo de $fetch com baseURL + Bearer token + tratamento de 401.
 *
 * Uso:
 *   const api = useApi()
 *   const data = await api<MyType>('/specialties')
 *   await api('/specialties', { method: 'POST', body: {...} })
 */
export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const baseURL = config.public.apiBaseUrl as string

  return async function api<T = unknown>(
    url: string,
    opts: Parameters<typeof $fetch>[1] = {},
  ): Promise<T> {
    const headers: Record<string, string> = {
      ...((opts.headers as Record<string, string>) || {}),
    }
    if (auth.accessToken) {
      headers.Authorization = `Bearer ${auth.accessToken}`
    }
    try {
      return await $fetch<T>(url, { baseURL, ...opts, headers })
    } catch (err: unknown) {
      const e = err as { status?: number; response?: { status?: number } }
      if (e?.status === 401 || e?.response?.status === 401) {
        auth.logout()
        await navigateTo('/login')
      }
      throw err
    }
  }
}

export function apiErrorMessage(err: unknown, fallback = 'Erro ao processar requisição'): string {
  const e = err as { data?: { detail?: string | unknown[] }; status?: number }
  const detail = e?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string }
    if (first?.msg) return first.msg
  }
  return fallback
}
