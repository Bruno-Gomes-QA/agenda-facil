export type UserRole = 'paciente' | 'recepcionista' | 'medico'

export interface UserOut {
  id: number
  name: string
  email: string
  role: UserRole
  phone: string | null
  is_active: boolean
}

export interface PatientCreate {
  name: string
  email: string
  password: string
  phone?: string
  cpf?: string
  birth_date?: string
}

export interface StaffCreate {
  name: string
  email: string
  password: string
  role: 'recepcionista' | 'medico'
  phone?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserOut
}
