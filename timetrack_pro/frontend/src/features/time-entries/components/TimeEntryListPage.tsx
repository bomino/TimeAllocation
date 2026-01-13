import { useState, useEffect } from 'react'
import { Plus, Square, Clock } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { format, endOfWeek, startOfWeek, subWeeks, subMonths, parseISO, isAfter, isBefore } from 'date-fns'
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
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import apiClient from '@/lib/api-client'
import { formatDate, formatDuration } from '@/lib/utils'
import type { TimeEntry, Timer } from '@/types/time-entry'
import { useAuth } from '@/features/auth/hooks/useAuth'

interface Project {
  id: number
  name: string
  status: string
}

function getEndOfCurrentWeek() {
  return endOfWeek(new Date(), { weekStartsOn: 1 })
}

function getMinAllowedDate(isAdmin: boolean) {
  const today = new Date()
  if (isAdmin) {
    return startOfWeek(subMonths(today, 1), { weekStartsOn: 1 })
  }
  return startOfWeek(subWeeks(today, 1), { weekStartsOn: 1 })
}

function createTimeEntrySchema(isAdmin: boolean) {
  const minDate = getMinAllowedDate(isAdmin)
  const maxDate = getEndOfCurrentWeek()

  return z.object({
    project_id: z.string().min(1, 'Project is required'),
    date: z.string().min(1, 'Date is required')
      .refine(
        (val) => {
          const entryDate = parseISO(val)
          return !isAfter(entryDate, maxDate)
        },
        'Cannot enter time for future weeks'
      )
      .refine(
        (val) => {
          const entryDate = parseISO(val)
          return !isBefore(entryDate, minDate)
        },
        isAdmin
          ? 'Cannot enter time older than 1 month'
          : 'Cannot enter time older than 1 week (contact admin for older entries)'
      ),
    hours: z.string().min(1, 'Hours is required').refine(
      (val) => parseFloat(val) > 0 && parseFloat(val) <= 24,
      'Hours must be between 0 and 24'
    ),
    description: z.string().optional(),
  })
}

type TimeEntryFormData = z.infer<ReturnType<typeof createTimeEntrySchema>>

export function TimeEntryListPage() {
  const queryClient = useQueryClient()
  const { isAdmin } = useAuth()
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)

  const timeEntrySchema = createTimeEntrySchema(isAdmin)
  const minAllowedDate = getMinAllowedDate(isAdmin)

  const form = useForm<TimeEntryFormData>({
    resolver: zodResolver(timeEntrySchema),
    defaultValues: {
      project_id: '',
      date: format(new Date(), 'yyyy-MM-dd'),
      hours: '',
      description: '',
    },
  })

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

  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await apiClient.get<{ success: boolean; data: Project[] }>('/projects/')
      return response.data.data ?? []
    },
  })

  const { data: activeTimer } = useQuery({
    queryKey: ['timer', 'active'],
    queryFn: async () => {
      const response = await apiClient.get<Timer>('/time-entries/timer/active/', {
        validateStatus: (status) => status === 200 || status === 404,
      })
      if (response.status === 404) return null
      return response.data
    },
    refetchInterval: (query) => (query.state.data ? 1000 : 30000),
  })

  const createEntryMutation = useMutation({
    mutationFn: async (data: TimeEntryFormData) => {
      const response = await apiClient.post('/time-entries/', {
        project_id: parseInt(data.project_id),
        date: data.date,
        hours: data.hours,
        description: data.description || '',
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-entries'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      setDialogOpen(false)
      form.reset({
        project_id: '',
        date: format(new Date(), 'yyyy-MM-dd'),
        hours: '',
        description: '',
      })
    },
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

  const onSubmit = (data: TimeEntryFormData) => {
    createEntryMutation.mutate(data)
  }

  if (isLoading) {
    return <PageLoader />
  }

  return (
    <div>
      <PageHeader
        title="Time Entries"
        description="Track your work hours"
        action={
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Entry
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Time Entry</DialogTitle>
                <DialogDescription>
                  Log your work hours for a project.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={form.handleSubmit(onSubmit)}>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="project">Project</Label>
                    <Select
                      value={form.watch('project_id')}
                      onValueChange={(value) => form.setValue('project_id', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a project" />
                      </SelectTrigger>
                      <SelectContent>
                        {projects?.map((project) => (
                          <SelectItem key={project.id} value={project.id.toString()}>
                            {project.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {form.formState.errors.project_id && (
                      <p className="text-sm text-destructive">{form.formState.errors.project_id.message}</p>
                    )}
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      min={format(minAllowedDate, 'yyyy-MM-dd')}
                      max={format(getEndOfCurrentWeek(), 'yyyy-MM-dd')}
                      {...form.register('date')}
                    />
                    {form.formState.errors.date && (
                      <p className="text-sm text-destructive">{form.formState.errors.date.message}</p>
                    )}
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="hours">Hours</Label>
                    <Input
                      id="hours"
                      type="number"
                      step="0.25"
                      min="0.25"
                      max="24"
                      placeholder="e.g., 2.5"
                      {...form.register('hours')}
                    />
                    {form.formState.errors.hours && (
                      <p className="text-sm text-destructive">{form.formState.errors.hours.message}</p>
                    )}
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="description">Description (optional)</Label>
                    <Input
                      id="description"
                      placeholder="What did you work on?"
                      {...form.register('description')}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createEntryMutation.isPending}>
                    {createEntryMutation.isPending ? 'Saving...' : 'Save Entry'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
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
                <Button onClick={() => setDialogOpen(true)}>
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
  const [elapsed, setElapsed] = useState(0)

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
