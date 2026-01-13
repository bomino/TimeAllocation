import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { z } from 'zod/v4'
import { zodResolver } from '@hookform/resolvers/zod'
import { Save } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { PageLoader } from '@/components/common/LoadingSpinner'
import apiClient from '@/lib/api-client'
import type { User } from '@/types/user'

const profileSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  timezone: z.string(),
  workflow_notifications_enabled: z.boolean(),
  security_notifications_enabled: z.boolean(),
})

type ProfileFormData = z.infer<typeof profileSchema>

export function ProfilePage() {
  const queryClient = useQueryClient()

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/users/me/')
      return response.data
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (data: ProfileFormData) => {
      const response = await apiClient.put<User>('/users/me/', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    values: profile
      ? {
          first_name: profile.first_name,
          last_name: profile.last_name,
          timezone: profile.timezone,
          workflow_notifications_enabled: profile.workflow_notifications_enabled,
          security_notifications_enabled: profile.security_notifications_enabled,
        }
      : undefined,
  })

  const onSubmit = (data: ProfileFormData) => {
    updateMutation.mutate(data)
  }

  if (isLoading) {
    return <PageLoader />
  }

  return (
    <div>
      <PageHeader
        title="Profile Settings"
        description="Manage your account settings and preferences"
      />

      <div className="max-w-2xl">
        <form onSubmit={handleSubmit(onSubmit)}>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-base">Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    {...register('first_name')}
                  />
                  {errors.first_name && (
                    <p className="text-sm text-destructive">{errors.first_name.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    {...register('last_name')}
                  />
                  {errors.last_name && (
                    <p className="text-sm text-destructive">{errors.last_name.message}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profile?.email || ''}
                  disabled
                  className="bg-muted"
                />
                <p className="text-xs text-muted-foreground">
                  Contact an administrator to change your email
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timezone">Timezone</Label>
                <Input
                  id="timezone"
                  {...register('timezone')}
                  placeholder="e.g., America/New_York"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-base">Notifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="workflow_notifications">Workflow Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications for timesheet approvals and comments
                  </p>
                </div>
                <input
                  type="checkbox"
                  id="workflow_notifications"
                  {...register('workflow_notifications_enabled')}
                  className="h-4 w-4"
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="security_notifications">Security Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications for login attempts and password changes
                  </p>
                </div>
                <input
                  type="checkbox"
                  id="security_notifications"
                  {...register('security_notifications_enabled')}
                  className="h-4 w-4"
                />
              </div>
            </CardContent>
          </Card>

          <Button type="submit" disabled={!isDirty || updateMutation.isPending}>
            <Save className="mr-2 h-4 w-4" />
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>
      </div>
    </div>
  )
}
