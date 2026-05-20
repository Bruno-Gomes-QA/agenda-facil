import type {
  Appointment,
  AppointmentCreate,
  AppointmentHistoryEntry,
} from '~/types/appointment'

export interface ListFilters {
  status?: string
  doctor_id?: number
  patient_id?: number
  from?: string
  to?: string
}

export function useAppointments() {
  const api = useApi()

  return {
    create: (data: AppointmentCreate) =>
      api<Appointment>('/appointments', { method: 'POST', body: data }),
    listMine: (filters: ListFilters = {}) =>
      api<Appointment[]>('/appointments/me', { query: filters }),
    listAll: (filters: ListFilters = {}) =>
      api<Appointment[]>('/appointments', { query: filters }),
    listDoctor: (params: { date?: string; from?: string; to?: string } = {}) =>
      api<Appointment[]>('/appointments/doctor/me', { query: params }),
    get: (id: number) => api<Appointment>(`/appointments/${id}`),
    reschedule: (id: number, scheduled_at: string) =>
      api<Appointment>(`/appointments/${id}`, { method: 'PATCH', body: { scheduled_at } }),
    cancel: (id: number) => api<Appointment>(`/appointments/${id}`, { method: 'DELETE' }),
    setStatus: (id: number, status: 'realizada' | 'no_show') =>
      api<Appointment>(`/appointments/${id}/status`, { method: 'PATCH', body: { status } }),
    setNotes: (id: number, doctor_notes: string) =>
      api<Appointment>(`/appointments/${id}/notes`, { method: 'PATCH', body: { doctor_notes } }),
    history: (id: number) =>
      api<AppointmentHistoryEntry[]>(`/appointments/${id}/history`),
  }
}
