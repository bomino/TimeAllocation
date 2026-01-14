import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Clock,
  FileText,
  BarChart3,
  Settings,
  Users,
  DollarSign,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { Button } from '@/components/ui/button'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const mainNavItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/time-entries', icon: Clock, label: 'Time Entries' },
  { to: '/timesheets', icon: FileText, label: 'Timesheets' },
]

const managerNavItems = [
  { to: '/reports', icon: BarChart3, label: 'Reports' },
]

const adminNavItems = [
  { to: '/admin/users', icon: Users, label: 'Users' },
  { to: '/admin/rates', icon: DollarSign, label: 'Rates' },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { isManager, isAdmin } = useAuth()

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-50 flex h-full w-60 flex-col bg-slate-900 text-slate-100 transition-transform duration-200 lg:static lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-14 items-center justify-between border-b border-slate-700 px-4">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-indigo-400" />
            <span className="font-semibold tracking-tight">TimeTrack Pro</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-slate-400 hover:bg-slate-800 hover:text-slate-100 lg:hidden"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {mainNavItems.map((item) => (
            <NavItem key={item.to} {...item} onClick={onClose} />
          ))}

          {isManager && (
            <>
              <div className="my-4 border-t border-slate-700" />
              <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Management
              </p>
              {managerNavItems.map((item) => (
                <NavItem key={item.to} {...item} onClick={onClose} />
              ))}
            </>
          )}

          {isAdmin && (
            <>
              <div className="my-4 border-t border-slate-700" />
              <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Admin
              </p>
              {adminNavItems.map((item) => (
                <NavItem key={item.to} {...item} onClick={onClose} />
              ))}
            </>
          )}
        </nav>

        <div className="border-t border-slate-700 p-3">
          <NavItem to="/profile" icon={Settings} label="Settings" onClick={onClose} />
        </div>
      </aside>
    </>
  )
}

interface NavItemProps {
  to: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  onClick?: () => void
}

function NavItem({ to, icon: Icon, label, onClick }: NavItemProps) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive
            ? 'bg-slate-800 text-white border-l-2 border-indigo-400'
            : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-100'
        )
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </NavLink>
  )
}
