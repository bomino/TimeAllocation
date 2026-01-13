import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { DollarSign, Plus, Pencil, Trash2 } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { format } from 'date-fns'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import apiClient from '@/lib/api-client'
import { formatDate } from '@/lib/utils'

interface Rate {
  id: number
  rate_type: 'EMPLOYEE_PROJECT' | 'PROJECT' | 'EMPLOYEE'
  hourly_rate: string
  effective_from: string
  effective_to: string | null
  employee: { id: number; first_name: string; last_name: string } | null
  project: { id: number; name: string } | null
  created_at: string
}

interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

interface Project {
  id: number
  name: string
}

const rateSchema = z.object({
  rate_type: z.enum(['EMPLOYEE_PROJECT', 'PROJECT', 'EMPLOYEE']),
  employee_id: z.string().optional(),
  project_id: z.string().optional(),
  hourly_rate: z.string().min(1, 'Hourly rate is required').refine(
    (val) => parseFloat(val) > 0,
    'Rate must be positive'
  ),
  effective_from: z.string().min(1, 'Start date is required'),
  effective_to: z.string().optional(),
})

type RateFormData = z.infer<typeof rateSchema>

const rateTypeLabels: Record<string, string> = {
  EMPLOYEE_PROJECT: 'Employee-Project',
  PROJECT: 'Project',
  EMPLOYEE: 'Employee',
}

const rateTypeColors: Record<string, 'default' | 'secondary' | 'destructive'> = {
  EMPLOYEE_PROJECT: 'default',
  PROJECT: 'secondary',
  EMPLOYEE: 'destructive',
}

export function RateManagement() {
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedRate, setSelectedRate] = useState<Rate | null>(null)
  const [editingRate, setEditingRate] = useState<Rate | null>(null)

  const form = useForm<RateFormData>({
    resolver: zodResolver(rateSchema),
    defaultValues: {
      rate_type: 'EMPLOYEE',
      employee_id: '',
      project_id: '',
      hourly_rate: '',
      effective_from: format(new Date(), 'yyyy-MM-dd'),
      effective_to: '',
    },
  })

  const rateType = form.watch('rate_type')

  const { data: rates, isLoading } = useQuery({
    queryKey: ['admin', 'rates'],
    queryFn: async () => {
      const response = await apiClient.get<{ success: boolean; data: Rate[] }>('/rates/')
      return response.data.data ?? []
    },
  })

  const { data: users } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: async () => {
      const response = await apiClient.get<{ success: boolean; data: User[] }>('/users/')
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

  const createMutation = useMutation({
    mutationFn: async (data: RateFormData) => {
      const payload = {
        rate_type: data.rate_type,
        hourly_rate: data.hourly_rate,
        effective_from: data.effective_from,
        effective_to: data.effective_to || null,
        employee_id: data.employee_id ? parseInt(data.employee_id) : null,
        project_id: data.project_id ? parseInt(data.project_id) : null,
      }
      const response = await apiClient.post('/rates/', payload)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'rates'] })
      handleCloseDialog()
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<RateFormData> }) => {
      const payload = {
        hourly_rate: data.hourly_rate,
        effective_from: data.effective_from,
        effective_to: data.effective_to || null,
      }
      const response = await apiClient.patch(`/rates/${id}/`, payload)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'rates'] })
      handleCloseDialog()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/rates/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'rates'] })
      setDeleteDialogOpen(false)
      setSelectedRate(null)
    },
  })

  const handleOpenCreate = () => {
    setEditingRate(null)
    form.reset({
      rate_type: 'EMPLOYEE',
      employee_id: '',
      project_id: '',
      hourly_rate: '',
      effective_from: format(new Date(), 'yyyy-MM-dd'),
      effective_to: '',
    })
    setDialogOpen(true)
  }

  const handleOpenEdit = (rate: Rate) => {
    setEditingRate(rate)
    form.reset({
      rate_type: rate.rate_type,
      employee_id: rate.employee?.id.toString() ?? '',
      project_id: rate.project?.id.toString() ?? '',
      hourly_rate: rate.hourly_rate,
      effective_from: rate.effective_from,
      effective_to: rate.effective_to ?? '',
    })
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingRate(null)
    form.reset()
  }

  const handleDeleteClick = (rate: Rate) => {
    setSelectedRate(rate)
    setDeleteDialogOpen(true)
  }

  const onSubmit = (data: RateFormData) => {
    if (editingRate) {
      updateMutation.mutate({ id: editingRate.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  if (isLoading) {
    return <PageLoader />
  }

  return (
    <div>
      <PageHeader
        title="Rate Management"
        description="Configure billing rates"
        action={
          <Button onClick={handleOpenCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Add Rate
          </Button>
        }
      />

      <Card>
        <CardContent className="p-0">
          {!rates || rates.length === 0 ? (
            <EmptyState
              icon={DollarSign}
              title="No rates configured"
              description="Add billing rates for employees and projects"
              action={
                <Button onClick={handleOpenCreate}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Rate
                </Button>
              }
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Employee</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead>Effective From</TableHead>
                  <TableHead>Effective To</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rates.map((rate) => (
                  <TableRow key={rate.id}>
                    <TableCell>
                      <Badge variant={rateTypeColors[rate.rate_type]}>
                        {rateTypeLabels[rate.rate_type]}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {rate.employee
                        ? `${rate.employee.first_name} ${rate.employee.last_name}`
                        : '-'}
                    </TableCell>
                    <TableCell>{rate.project?.name ?? '-'}</TableCell>
                    <TableCell className="text-right font-medium">
                      ${parseFloat(rate.hourly_rate).toFixed(2)}/hr
                    </TableCell>
                    <TableCell>{formatDate(rate.effective_from)}</TableCell>
                    <TableCell>
                      {rate.effective_to ? formatDate(rate.effective_to) : 'Ongoing'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleOpenEdit(rate)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDeleteClick(rate)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingRate ? 'Edit Rate' : 'Add Rate'}</DialogTitle>
            <DialogDescription>
              {editingRate
                ? 'Update the billing rate configuration.'
                : 'Create a new billing rate for an employee or project.'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid gap-4 py-4">
              {!editingRate && (
                <div className="grid gap-2">
                  <Label>Rate Type</Label>
                  <Select
                    value={form.watch('rate_type')}
                    onValueChange={(value) =>
                      form.setValue('rate_type', value as RateFormData['rate_type'])
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select rate type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="EMPLOYEE">Employee Default</SelectItem>
                      <SelectItem value="PROJECT">Project Default</SelectItem>
                      <SelectItem value="EMPLOYEE_PROJECT">Employee-Project Specific</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {!editingRate && (rateType === 'EMPLOYEE' || rateType === 'EMPLOYEE_PROJECT') && (
                <div className="grid gap-2">
                  <Label>Employee</Label>
                  <Select
                    value={form.watch('employee_id')}
                    onValueChange={(value) => form.setValue('employee_id', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select employee" />
                    </SelectTrigger>
                    <SelectContent>
                      {users?.map((user) => (
                        <SelectItem key={user.id} value={user.id.toString()}>
                          {user.first_name} {user.last_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {form.formState.errors.employee_id && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.employee_id.message}
                    </p>
                  )}
                </div>
              )}

              {!editingRate && (rateType === 'PROJECT' || rateType === 'EMPLOYEE_PROJECT') && (
                <div className="grid gap-2">
                  <Label>Project</Label>
                  <Select
                    value={form.watch('project_id')}
                    onValueChange={(value) => form.setValue('project_id', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select project" />
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
                    <p className="text-sm text-destructive">
                      {form.formState.errors.project_id.message}
                    </p>
                  )}
                </div>
              )}

              <div className="grid gap-2">
                <Label htmlFor="hourly_rate">Hourly Rate ($)</Label>
                <Input
                  id="hourly_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="e.g., 75.00"
                  {...form.register('hourly_rate')}
                />
                {form.formState.errors.hourly_rate && (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.hourly_rate.message}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="effective_from">Effective From</Label>
                  <Input id="effective_from" type="date" {...form.register('effective_from')} />
                  {form.formState.errors.effective_from && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.effective_from.message}
                    </p>
                  )}
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="effective_to">Effective To (optional)</Label>
                  <Input id="effective_to" type="date" {...form.register('effective_to')} />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleCloseDialog}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {createMutation.isPending || updateMutation.isPending
                  ? 'Saving...'
                  : editingRate
                    ? 'Update Rate'
                    : 'Create Rate'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Rate</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this rate? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => selectedRate && deleteMutation.mutate(selectedRate.id)}
              disabled={deleteMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
