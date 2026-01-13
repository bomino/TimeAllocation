import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, UserX, Search } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Label } from '@/components/ui/label'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import apiClient from '@/lib/api-client'
import { formatDate } from '@/lib/utils'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'EMPLOYEE' | 'MANAGER' | 'ADMIN'
  is_active: boolean
  created_at: string
  last_login: string | null
}

interface DeactivationStatus {
  can_deactivate: boolean
  pending_timesheets_count: number
  user_id: number
}

const roleColors: Record<string, 'default' | 'secondary' | 'destructive'> = {
  EMPLOYEE: 'secondary',
  MANAGER: 'default',
  ADMIN: 'destructive',
}

export function UserManagement() {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [deactivationReason, setDeactivationReason] = useState('')
  const [forceDeactivate, setForceDeactivate] = useState(false)

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: async () => {
      const response = await apiClient.get<{ success: boolean; data: User[] }>('/users/')
      return response.data.data ?? []
    },
  })

  const { data: deactivationStatus, refetch: refetchStatus } = useQuery({
    queryKey: ['admin', 'deactivation-status', selectedUser?.id],
    queryFn: async () => {
      if (!selectedUser) return null
      const response = await apiClient.get<DeactivationStatus>(
        `/users/${selectedUser.id}/deactivation-status/`
      )
      return response.data
    },
    enabled: !!selectedUser,
  })

  const deactivateMutation = useMutation({
    mutationFn: async ({ userId, reason, force }: { userId: number; reason: string; force: boolean }) => {
      const response = await apiClient.post(`/users/${userId}/deactivate/`, {
        reason,
        force,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
      setDeactivateDialogOpen(false)
      setSelectedUser(null)
      setDeactivationReason('')
      setForceDeactivate(false)
    },
  })

  const handleDeactivateClick = (user: User) => {
    setSelectedUser(user)
    setDeactivateDialogOpen(true)
    refetchStatus()
  }

  const handleConfirmDeactivate = () => {
    if (!selectedUser || !deactivationReason.trim()) return
    deactivateMutation.mutate({
      userId: selectedUser.id,
      reason: deactivationReason,
      force: forceDeactivate,
    })
  }

  const filteredUsers = users?.filter(
    (user) =>
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (isLoading) {
    return <PageLoader />
  }

  return (
    <div>
      <PageHeader title="User Management" description="View and manage system users" />

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search users by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {!filteredUsers || filteredUsers.length === 0 ? (
            <EmptyState
              icon={Users}
              title="No users found"
              description={searchTerm ? 'Try adjusting your search' : 'No users in the system'}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">
                      {user.first_name} {user.last_name}
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant={roleColors[user.role]}>{user.role}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={user.is_active ? 'default' : 'secondary'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {user.last_login ? formatDate(user.last_login) : 'Never'}
                    </TableCell>
                    <TableCell className="text-right">
                      {user.is_active && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeactivateClick(user)}
                        >
                          <UserX className="h-4 w-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={deactivateDialogOpen} onOpenChange={setDeactivateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Deactivate User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to deactivate{' '}
              <strong>
                {selectedUser?.first_name} {selectedUser?.last_name}
              </strong>
              ? This action will export their data and prevent them from logging in.
            </AlertDialogDescription>
          </AlertDialogHeader>

          {deactivationStatus && !deactivationStatus.can_deactivate && (
            <div className="rounded-md bg-yellow-50 p-4 text-sm text-yellow-800">
              <p className="font-medium">Warning: Pending timesheets</p>
              <p>
                This user has {deactivationStatus.pending_timesheets_count} pending timesheet(s).
                You can force deactivation, but it&apos;s recommended to resolve these first.
              </p>
              <label className="mt-2 flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={forceDeactivate}
                  onChange={(e) => setForceDeactivate(e.target.checked)}
                  className="rounded"
                />
                <span>Force deactivation anyway</span>
              </label>
            </div>
          )}

          <div className="grid gap-2">
            <Label htmlFor="reason">Reason for deactivation</Label>
            <Input
              id="reason"
              placeholder="e.g., Employee left the company"
              value={deactivationReason}
              onChange={(e) => setDeactivationReason(e.target.value)}
            />
          </div>

          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDeactivate}
              disabled={
                !deactivationReason.trim() ||
                deactivateMutation.isPending ||
                !!(deactivationStatus && !deactivationStatus.can_deactivate && !forceDeactivate)
              }
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deactivateMutation.isPending ? 'Deactivating...' : 'Deactivate'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
