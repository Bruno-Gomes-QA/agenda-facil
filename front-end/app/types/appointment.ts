import type { DoctorPublic } from './doctor'
import type { UserOut } from './auth'

export type AppointmentStatus = 'agendada' | 'cancelada' | 'realizada' | 'no_show'

export interface Appointment {
  id: number
  patient: UserOut
  doctor: DoctorPublic
  scheduled_at: string
  duration_min: number
  status: AppointmentStatus
  reason: string | null
  created_at: string
  rescheduled_at: string | null
  cancelled_at: string | null
  cancelled_by: number | null
  created_by: number | null
  doctor_notes: string | null
}

export interface AppointmentCreate {
  doctor_id: number
  scheduled_at: string
  reason?: string
  patient_id?: number
}

export interface AppointmentHistoryEntry {
  id: number
  appointment_id: number
  changed_by: number | null
  from_status: string | null
  to_status: string | null
  note: string | null
  changed_at: string
}
