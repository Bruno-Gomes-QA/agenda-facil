import type {
  AdminPatientCreate,
  AdminPatientCreateResponse,
  AdminPatientUpdate,
} from '~/types/admin'
import type { UserOut } from '~/types/auth'

export function useAdminPatients() {
  const api = useApi()

  return {
    list: (search?: string) =>
      api<UserOut[]>('/admin/patients', { query: search ? { search } : {} }),
    get: (id: number) => api<UserOut>(`/admin/patients/${id}`),
    create: (data: AdminPatientCreate) =>
      api<AdminPatientCreateResponse>('/admin/patients', { method: 'POST', body: data }),
    update: (id: number, data: AdminPatientUpdate) =>
      api<UserOut>(`/admin/patients/${id}`, { method: 'PATCH', body: data }),
  }
}
