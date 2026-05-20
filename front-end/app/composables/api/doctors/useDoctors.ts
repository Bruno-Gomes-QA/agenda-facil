import type { Doctor, DoctorCreate, DoctorPublic, DoctorUpdate } from '~/types/doctor'

export function useDoctors() {
  const api = useApi()

  return {
    list: (filters: { specialty_id?: number; search?: string; include_inactive?: boolean } = {}) =>
      api<DoctorPublic[]>('/doctors', { query: filters }),
    get: (id: number) => api<DoctorPublic>(`/doctors/${id}`),
    getMe: () => api<Doctor>('/doctors/me'),
    getFull: (id: number) => api<Doctor>(`/doctors/admin/${id}`),
    create: (data: DoctorCreate) => api<Doctor>('/doctors', { method: 'POST', body: data }),
    update: (id: number, data: DoctorUpdate) =>
      api<Doctor>(`/doctors/${id}`, { method: 'PATCH', body: data }),
    remove: (id: number) => api<Doctor>(`/doctors/${id}`, { method: 'DELETE' }),
  }
}
