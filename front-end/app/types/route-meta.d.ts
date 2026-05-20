import 'vue-router'
import type { UserRole } from './auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiredRoles?: UserRole[]
  }
}

export {}
