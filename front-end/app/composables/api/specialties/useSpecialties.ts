import type { Specialty, SpecialtyCreate, SpecialtyUpdate } from '~/types/specialty'

export function useSpecialties() {
  const api = useApi()

  return {
    list: (includeInactive = false) =>
      api<Specialty[]>('/specialties', {
        query: { include_inactive: includeInactive },
      }),
    get: (id: number) => api<Specialty>(`/specialties/${id}`),
    create: (data: SpecialtyCreate) =>
      api<Specialty>('/specialties', { method: 'POST', body: data }),
    update: (id: number, data: SpecialtyUpdate) =>
      api<Specialty>(`/specialties/${id}`, { method: 'PATCH', body: data }),
    remove: (id: number) =>
      api<Specialty>(`/specialties/${id}`, { method: 'DELETE' }),
  }
}
