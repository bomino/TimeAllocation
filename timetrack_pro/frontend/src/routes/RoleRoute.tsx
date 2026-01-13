import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/features/auth/hooks/useAuth'
import type { UserRole } from '@/lib/constants'
import { USER_ROLE } from '@/lib/constants'

interface RoleRouteProps {
  allowedRoles: UserRole[]
}

export function RoleRoute({ allowedRoles }: RoleRouteProps) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export function ManagerRoute() {
  return <RoleRoute allowedRoles={[USER_ROLE.MANAGER, USER_ROLE.ADMIN]} />
}

export function AdminRoute() {
  return <RoleRoute allowedRoles={[USER_ROLE.ADMIN]} />
}
