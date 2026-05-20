/**
 * useApiFetch — wrapper de useFetch com injeção automática de token Bearer
 * e tratamento de 401 (redireciona para /login).
 *
 * Uso idêntico ao useFetch nativo do Nuxt.
 */
export function useApiFetch<T>(
  url: string | Ref<string> | (() => string),
  opts?: Parameters<typeof useFetch<T>>[1],
) {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  return useFetch<T>(url, {
    baseURL: config.public.apiBaseUrl as string,
    ...opts,
    onRequest({ options }) {
      const token = auth.accessToken
      if (token) {
        const existing = (options.headers || {}) as Record<string, string>
        options.headers = { ...existing, Authorization: `Bearer ${token}` }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        auth.logout()
        navigateTo('/login')
      }
    },
  })
}
