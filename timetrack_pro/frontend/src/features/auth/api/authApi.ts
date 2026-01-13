import apiClient from '@/lib/api-client'
import type { PasswordResetRequest, PasswordResetConfirm } from '@/types/user'

export const authApi = {
  requestPasswordReset: async (data: PasswordResetRequest) => {
    const response = await apiClient.post('/auth/password/reset/', data)
    return response.data
  },

  confirmPasswordReset: async (data: PasswordResetConfirm) => {
    const response = await apiClient.post('/auth/password/reset/confirm/', data)
    return response.data
  },
}
