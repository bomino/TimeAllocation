import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Check, X, MessageSquare } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { useAuth } from '@/features/auth/hooks/useAuth'
import apiClient from '@/lib/api-client'
import { formatDate, formatDateTime } from '@/lib/utils'
import type { Timesheet } from '@/types/timesheet'
import type { TimesheetStatus } from '@/lib/constants'

const statusVariant: Record<TimesheetStatus, 'draft' | 'submitted' | 'approved' | 'rejected'> = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
}

export function TimesheetDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, isManager } = useAuth()

  const { data: timesheet, isLoading } = useQuery({
    queryKey: ['timesheet', id],
    queryFn: async () => {
      const response = await apiClient.get<Timesheet>(`/timesheets/${id}/`)
      return response.data
    },
    enabled: !!id,
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/timesheets/${id}/submit/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timesheet', id] })
      queryClient.invalidateQueries({ queryKey: ['timesheets'] })
    },
  })

  const approveMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/timesheets/${id}/approve/`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timesheet', id] })
      queryClient.invalidateQueries({ queryKey: ['timesheets'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: async (comment: string) => {
      const response = await apiClient.post(`/timesheets/${id}/reject/`, { comment })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timesheet', id] })
      queryClient.invalidateQueries({ queryKey: ['timesheets'] })
    },
  })

  if (isLoading || !timesheet) {
    return <PageLoader />
  }

  const isOwner = timesheet.user.id === user?.id
  const canSubmit = isOwner && timesheet.status === 'DRAFT'
  const canApprove = isManager && !isOwner && timesheet.status === 'SUBMITTED'

  return (
    <div>
      <Button
        variant="ghost"
        className="mb-4"
        onClick={() => navigate('/timesheets')}
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Timesheets
      </Button>

      <PageHeader
        title={`Week of ${formatDate(timesheet.week_start)}`}
        description={`${timesheet.user.first_name} ${timesheet.user.last_name}`}
        action={
          <div className="flex gap-2">
            {canSubmit && (
              <Button onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending}>
                <Send className="mr-2 h-4 w-4" />
                Submit
              </Button>
            )}
            {canApprove && (
              <>
                <Button
                  variant="outline"
                  onClick={() => {
                    const comment = prompt('Rejection reason:')
                    if (comment) rejectMutation.mutate(comment)
                  }}
                  disabled={rejectMutation.isPending}
                >
                  <X className="mr-2 h-4 w-4" />
                  Reject
                </Button>
                <Button onClick={() => approveMutation.mutate()} disabled={approveMutation.isPending}>
                  <Check className="mr-2 h-4 w-4" />
                  Approve
                </Button>
              </>
            )}
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Time Entries</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {timesheet.entries.length === 0 ? (
                <div className="p-6 text-center text-muted-foreground">
                  No time entries for this week
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Project</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Hours</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {timesheet.entries.map((entry) => (
                      <TableRow key={entry.id}>
                        <TableCell>{formatDate(entry.date)}</TableCell>
                        <TableCell>{entry.project.name}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {entry.description || '-'}
                        </TableCell>
                        <TableCell className="text-right">
                          {parseFloat(entry.hours).toFixed(2)}h
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {timesheet.comments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Comments
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {timesheet.comments.map((comment) => (
                    <div key={comment.id} className="border-l-2 border-muted pl-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">
                          {comment.author.first_name} {comment.author.last_name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {formatDateTime(comment.created_at)}
                        </span>
                      </div>
                      <p className="text-sm">{comment.text}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <Badge variant={statusVariant[timesheet.status]}>
                  {timesheet.status.toLowerCase()}
                </Badge>
              </div>
              <Separator />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Hours</span>
                <span className="font-medium">{parseFloat(timesheet.total_hours).toFixed(1)}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Entries</span>
                <span className="font-medium">{timesheet.entries.length}</span>
              </div>
              {timesheet.submitted_at && (
                <>
                  <Separator />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Submitted</span>
                    <span className="text-sm">{formatDateTime(timesheet.submitted_at)}</span>
                  </div>
                </>
              )}
              {timesheet.approved_at && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Approved</span>
                  <span className="text-sm">{formatDateTime(timesheet.approved_at)}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
