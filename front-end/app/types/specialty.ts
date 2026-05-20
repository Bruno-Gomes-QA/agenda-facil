export interface Specialty {
  id: number
  name: string
  description: string | null
  is_active: boolean
}

export interface SpecialtyCreate {
  name: string
  description?: string | null
}

export interface SpecialtyUpdate {
  name?: string
  description?: string | null
  is_active?: boolean
}
