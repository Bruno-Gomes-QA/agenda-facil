import type { Specialty } from './specialty'

export interface DoctorPublic {
  id: number
  name: string
  crm: string
  bio: string | null
  is_active: boolean
  specialty: Specialty
}

export interface Doctor extends DoctorPublic {
  email: string
  phone: string | null
  user_id: number
}

export interface DoctorCreate {
  name: string
  email: string
  password: string
  phone?: string
  specialty_id: number
  crm: string
  bio?: string
}

export interface DoctorUpdate {
  name?: string
  phone?: string
  specialty_id?: number
  bio?: string
  is_active?: boolean
}
