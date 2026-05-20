import type {
  AvailabilityResponse,
  AvailabilityRule,
  AvailabilityRuleCreate,
} from '~/types/availability'

export function useAvailability() {
  const api = useApi()

  return {
    listRules: (doctorId: number) =>
      api<AvailabilityRule[]>(`/doctors/${doctorId}/availability-rules`),
    createRule: (doctorId: number, data: AvailabilityRuleCreate) =>
      api<AvailabilityRule>(`/doctors/${doctorId}/availability-rules`, {
        method: 'POST',
        body: data,
      }),
    deleteRule: (doctorId: number, ruleId: number) =>
      api<void>(`/doctors/${doctorId}/availability-rules/${ruleId}`, { method: 'DELETE' }),
    getSlots: (doctorId: number, date: string) =>
      api<AvailabilityResponse>(`/doctors/${doctorId}/availability`, {
        query: { date },
      }),
  }
}
