import { Clock, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { MetricsCard } from './MetricsCard'
import { WeeklyHoursChart } from './WeeklyHoursChart'
import { RecentTimesheets } from './RecentTimesheets'
import { useDashboardData } from '../hooks/useDashboardData'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

export function DashboardPage() {
  const { user, isManager } = useAuth()
  const { data, isLoading } = useDashboardData()

  if (isLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.first_name || 'User'}`}
        description="Here's an overview of your time tracking"
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <MetricsCard
          title="Hours This Week"
          value={`${data?.totalHoursThisWeek || 0}h`}
          description="of 40h target"
          icon={Clock}
        />
        <MetricsCard
          title="Timesheets"
          value={data?.recentTimesheets?.length || 0}
          description="total timesheets"
          icon={FileText}
        />
        {isManager && (
          <>
            <MetricsCard
              title="Pending Approval"
              value={data?.pendingTimesheetsCount || 0}
              description="awaiting review"
              icon={AlertCircle}
            />
            <MetricsCard
              title="Approved This Week"
              value={0}
              description="timesheets approved"
              icon={CheckCircle}
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <WeeklyHoursChart data={data?.weeklyHours || []} />
        <RecentTimesheets timesheets={data?.recentTimesheets || []} />
      </div>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div>
      <div className="mb-6">
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-48" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-1" />
              <Skeleton className="h-3 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[200px]" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
