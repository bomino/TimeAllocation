import { useState } from 'react'
import { Plus, Square, Clock } from 'lucide-react'
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
import { Input } from '@/components/ui/input'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import apiClient from '@/lib/api-client'
import { formatDate, formatDuration } from '@/lib/utils'
import type { TimeEntry, Timer } from '@/types/time-entry'
import { useEffect, useState as useTimerState } from 'react'

export function TimeEntryListPage() {
  const queryClient = useQueryClient()
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const { data: entries, isLoading } = useQuery({
    queryKey: ['time-entries', { dateFrom, dateTo }],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      const response = await apiClient.get<{ success: boolean; data: TimeEntry[]; meta: object }>('/time-entries/', { params })
      return response.data.data ?? []
    },
  })

  const { data: activeTimer } = useQuery({
    queryKey: ['timer', 'active'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Timer>('/time-entries/timer/active/')
        return response.data
      } catch {
        return null
      }
    },
    refetchInterval: 1000,
  })

  const stopTimerMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/time-entries/timer/stop/')
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-entries'] })
      queryClient.invalidateQueries({ queryKey: ['timer'] })
    },
  })

  if (isLoading) {
    return <PageLoader />
  }

  return (
    <div>
      <PageHeader
        title="Time Entries"
        description="Track your work hours"
        action={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Entry
          </Button>
        }
      />

      {activeTimer && (
        <Card className="mb-6 border-primary">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              Timer Running
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{activeTimer.project.name}</p>
                <p className="text-sm text-muted-foreground">{activeTimer.description || 'No description'}</p>
              </div>
              <div className="flex items-center gap-4">
                <TimerDisplay startTime={activeTimer.timer_started_at} />
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => stopTimerMutation.mutate()}
                  disabled={stopTimerMutation.isPending}
                >
                  <Square className="mr-2 h-4 w-4" />
                  Stop
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                placeholder="From date"
              />
            </div>
            <div className="flex-1">
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                placeholder="To date"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {!entries || entries.length === 0 ? (
            <EmptyState
              icon={Clock}
              title="No time entries"
              description="Start tracking your time by adding an entry or starting a timer"
              action={
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Entry
                </Button>
              }
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Hours</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{formatDate(entry.date)}</TableCell>
                    <TableCell>{entry.project.name}</TableCell>
                    <TableCell className="max-w-xs truncate">
                      {entry.description || '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {entry.is_timer_entry && (
                        <Badge variant="outline" className="mr-2">
                          Timer
                        </Badge>
                      )}
                      {parseFloat(entry.hours).toFixed(2)}h
                    </TableCell>
                    <TableCell className="text-right">
                      ${parseFloat(entry.billing_rate).toFixed(2)}/h
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

function TimerDisplay({ startTime }: { startTime: string }) {
  const [elapsed, setElapsed] = useTimerState(0)

  useEffect(() => {
    const start = new Date(startTime).getTime()
    const updateElapsed = () => {
      const now = Date.now()
      setElapsed(Math.floor((now - start) / 1000))
    }
    updateElapsed()
    const interval = setInterval(updateElapsed, 1000)
    return () => clearInterval(interval)
  }, [startTime])

  return (
    <div className="text-2xl font-mono font-bold text-primary">
      {formatDuration(elapsed)}
    </div>
  )
}
