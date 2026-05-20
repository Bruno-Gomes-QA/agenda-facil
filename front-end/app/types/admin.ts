import type { UserOut } from './auth'

export interface AdminPatientCreate {
  name: string
  email: string
  password?: string
  phone?: string
  cpf?: string
}

export interface AdminPatientCreateResponse {
  user: UserOut
  generated_password: string | null
}

export interface AdminPatientUpdate {
  name?: string
  phone?: string
  is_active?: boolean
}
