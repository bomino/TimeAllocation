import type { UserRole } from '@/lib/constants'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: UserRole
  timezone: string
  workflow_notifications_enabled: boolean
  security_notifications_enabled: boolean
  company?: {
    id: number
    name: string
  }
  manager?: {
    id: number
    email: string
    first_name: string
    last_name: string
  }
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  uid: string
  token: string
  new_password: string
  confirm_password: string
}
