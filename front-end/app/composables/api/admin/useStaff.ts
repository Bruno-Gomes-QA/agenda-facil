import type { StaffCreate, UserOut } from '~/types/auth'

export function useStaff() {
  const api = useApi()

  return {
    create: (data: StaffCreate) => api<UserOut>('/users/staff', { method: 'POST', body: data }),
  }
}
