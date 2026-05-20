export interface AvailabilityRule {
  id: number
  doctor_id: number
  weekday: number
  start_time: string
  end_time: string
}

export interface AvailabilityRuleCreate {
  weekday: number
  start_time: string
  end_time: string
}

export interface AvailabilitySlot {
  datetime: string
  available: boolean
}

export interface AvailabilityResponse {
  doctor_id: number
  date: string
  slot_duration_min: number
  slots: AvailabilitySlot[]
}
