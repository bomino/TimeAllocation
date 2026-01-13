import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, ChevronRight } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import apiClient from '@/lib/api-client'
import { formatDate } from '@/lib/utils'
import type { TimesheetListItem } from '@/types/timesheet'
import type { TimesheetStatus } from '@/lib/constants'

const statusVariant: Record<TimesheetStatus, 'draft' | 'submitted' | 'approved' | 'rejected'> = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
}

export function TimesheetListPage() {
  const { isManager } = useAuth()
  const [viewTeam, setViewTeam] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['timesheets', { viewTeam, statusFilter }],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (viewTeam && isManager) params.view = 'team'
      if (statusFilter) params.status = statusFilter
      const response = await apiClient.get<{ data: TimesheetListItem[] }>('/timesheets/', { params })
      return response.data.data || []
    },
  })

  if (isLoading) {
    return <PageLoader />
  }

  const timesheets = data || []

  return (
    <div>
      <PageHeader
        title="Timesheets"
        description="View and manage your weekly timesheets"
      />

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex gap-2">
              <Button
                variant={statusFilter === '' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('')}
              >
                All
              </Button>
              <Button
                variant={statusFilter === 'DRAFT' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('DRAFT')}
              >
                Draft
              </Button>
              <Button
                variant={statusFilter === 'SUBMITTED' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('SUBMITTED')}
              >
                Submitted
              </Button>
              <Button
                variant={statusFilter === 'APPROVED' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('APPROVED')}
              >
                Approved
              </Button>
              <Button
                variant={statusFilter === 'REJECTED' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('REJECTED')}
              >
                Rejected
              </Button>
            </div>

            {isManager && (
              <div className="ml-auto">
                <Button
                  variant={viewTeam ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewTeam(!viewTeam)}
                >
                  {viewTeam ? 'My Timesheets' : 'Team View'}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {timesheets.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No timesheets found"
              description="Timesheets will appear here once created"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  {viewTeam && <TableHead>Employee</TableHead>}
                  <TableHead>Week</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Total Hours</TableHead>
                  <TableHead className="text-right">Submitted</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {timesheets.map((timesheet) => (
                  <TableRow key={timesheet.id}>
                    {viewTeam && (
                      <TableCell>
                        {timesheet.user.first_name} {timesheet.user.last_name}
                      </TableCell>
                    )}
                    <TableCell className="font-medium">
                      {formatDate(timesheet.week_start)}
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[timesheet.status]}>
                        {timesheet.status.toLowerCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {parseFloat(timesheet.total_hours).toFixed(1)}h
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {timesheet.submitted_at ? formatDate(timesheet.submitted_at) : '-'}
                    </TableCell>
                    <TableCell>
                      <Link to={`/timesheets/${timesheet.id}`}>
                        <Button variant="ghost" size="sm">
                          View
                          <ChevronRight className="ml-1 h-4 w-4" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
