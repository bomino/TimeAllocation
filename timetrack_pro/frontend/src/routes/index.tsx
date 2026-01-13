import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { ManagerRoute, AdminRoute } from './RoleRoute'
import { LoginForm } from '@/features/auth/components/LoginForm'
import { PasswordResetForm } from '@/features/auth/components/PasswordResetForm'
import { DashboardPage } from '@/features/dashboard/components/DashboardPage'
import { TimeEntryListPage } from '@/features/time-entries/components/TimeEntryListPage'
import { TimesheetListPage } from '@/features/timesheets/components/TimesheetListPage'
import { TimesheetDetailPage } from '@/features/timesheets/components/TimesheetDetailPage'
import { ReportsPage } from '@/features/reports/components/ReportsPage'
import { AdminPage } from '@/features/admin/components/AdminPage'
import { UserManagement } from '@/features/admin/components/UserManagement'
import { RateManagement } from '@/features/admin/components/RateManagement'
import { ProfilePage } from '@/features/profile/components/ProfilePage'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginForm />,
  },
  {
    path: '/forgot-password',
    element: <PasswordResetForm />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            element: <Navigate to="/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: <DashboardPage />,
          },
          {
            path: 'time-entries',
            element: <TimeEntryListPage />,
          },
          {
            path: 'timesheets',
            element: <TimesheetListPage />,
          },
          {
            path: 'timesheets/:id',
            element: <TimesheetDetailPage />,
          },
          {
            path: 'profile',
            element: <ProfilePage />,
          },
          {
            element: <ManagerRoute />,
            children: [
              {
                path: 'reports',
                element: <ReportsPage />,
              },
            ],
          },
          {
            element: <AdminRoute />,
            children: [
              {
                path: 'admin',
                element: <AdminPage />,
              },
              {
                path: 'admin/users',
                element: <UserManagement />,
              },
              {
                path: 'admin/rates',
                element: <RateManagement />,
              },
            ],
          },
        ],
      },
    ],
  },
])
