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
import { Separator } from '@/components/ui/separator'

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
          'fixed left-0 top-0 z-50 flex h-full w-64 flex-col border-r bg-background transition-transform duration-200 lg:static lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-16 items-center justify-between border-b px-4">
          <div className="flex items-center gap-2 text-primary">
            <Clock className="h-6 w-6" />
            <span className="font-bold">TimeTrack Pro</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-4">
          {mainNavItems.map((item) => (
            <NavItem key={item.to} {...item} onClick={onClose} />
          ))}

          {isManager && (
            <>
              <Separator className="my-4" />
              <p className="mb-2 px-3 text-xs font-semibold uppercase text-muted-foreground">
                Management
              </p>
              {managerNavItems.map((item) => (
                <NavItem key={item.to} {...item} onClick={onClose} />
              ))}
            </>
          )}

          {isAdmin && (
            <>
              <Separator className="my-4" />
              <p className="mb-2 px-3 text-xs font-semibold uppercase text-muted-foreground">
                Admin
              </p>
              {adminNavItems.map((item) => (
                <NavItem key={item.to} {...item} onClick={onClose} />
              ))}
            </>
          )}
        </nav>

        <div className="border-t p-4">
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
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        )
      }
    >
      <Icon className="h-5 w-5" />
      {label}
    </NavLink>
  )
}
