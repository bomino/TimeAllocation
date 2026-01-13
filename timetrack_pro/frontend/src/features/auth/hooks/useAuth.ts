import { useAuthStore } from '../stores/authStore'
import { USER_ROLE } from '@/lib/constants'

export function useAuth() {
  const { user, isAuthenticated, isLoading, error, login, logout, clearError } = useAuthStore()

  const isAdmin = user?.role === USER_ROLE.ADMIN
  const isManager = user?.role === USER_ROLE.MANAGER || isAdmin
  const isEmployee = user?.role === USER_ROLE.EMPLOYEE

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    isAdmin,
    isManager,
    isEmployee,
    login,
    logout,
    clearError,
  }
}
