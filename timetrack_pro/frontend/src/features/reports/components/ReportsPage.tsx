import { useState, useEffect } from 'react'
import { BarChart3, PieChart, Users } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPie,
  Pie,
  Cell,
} from 'recharts'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import apiClient from '@/lib/api-client'
import { format, subDays } from 'date-fns'

interface HoursSummary {
  total_hours: string
  entry_count: number
  by_user?: Array<{ user_id: number; email: string; name: string; total_hours: string }>
  by_project?: Array<{ project_id: number; project_name: string; total_hours: string }>
}

interface ApprovalMetrics {
  total_timesheets: number
  draft_count: number
  submitted_count: number
  approved_count: number
  rejected_count: number
  approval_rate: number
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function ReportsPage() {
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'))
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [chartsReady, setChartsReady] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setChartsReady(true), 100)
    return () => clearTimeout(timer)
  }, [])

  const { data: hoursSummary, isLoading: hoursLoading } = useQuery({
    queryKey: ['reports', 'hours', { startDate, endDate }],
    queryFn: async () => {
      const response = await apiClient.get<HoursSummary>('/reports/hours/summary/', {
        params: { start_date: startDate, end_date: endDate, group_by: 'user,project' },
      })
      return response.data
    },
  })

  const { data: approvalMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['reports', 'approval', { startDate, endDate }],
    queryFn: async () => {
      const response = await apiClient.get<ApprovalMetrics>('/reports/approval/metrics/', {
        params: { start_date: startDate, end_date: endDate },
      })
      return response.data
    },
  })

  const pieData = approvalMetrics
    ? [
        { name: 'Draft', value: approvalMetrics.draft_count },
        { name: 'Submitted', value: approvalMetrics.submitted_count },
        { name: 'Approved', value: approvalMetrics.approved_count },
        { name: 'Rejected', value: approvalMetrics.rejected_count },
      ].filter((d) => d.value > 0)
    : []

  return (
    <div>
      <PageHeader
        title="Reports"
        description="Analytics and insights for your team"
      />

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Users className="h-4 w-4" />
              Hours by User
            </CardTitle>
          </CardHeader>
          <CardContent>
            {hoursLoading || !chartsReady ? (
              <Skeleton className="h-[250px]" />
            ) : !hoursSummary?.by_user?.length ? (
              <div className="h-[250px] flex items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            ) : (
              <div className="h-[250px]" style={{ minWidth: 0 }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={200}>
                  <BarChart
                    data={hoursSummary.by_user.map((u) => ({
                      name: u.name || u.email.split('@')[0],
                      hours: parseFloat(u.total_hours),
                    }))}
                    layout="vertical"
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={100}
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '12px',
                      }}
                      formatter={(value) => [`${Number(value).toFixed(1)}h`, 'Hours']}
                    />
                    <Bar dataKey="hours" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              Timesheet Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading || !chartsReady ? (
              <Skeleton className="h-[250px]" />
            ) : pieData.length === 0 ? (
              <div className="h-[250px] flex items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            ) : (
              <div className="h-[250px]" style={{ minWidth: 0 }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={200}>
                  <RechartsPie>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    >
                      {pieData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
            )}
            {approvalMetrics && (
              <div className="mt-4 text-center">
                <p className="text-2xl font-bold text-primary">
                  {approvalMetrics.approval_rate.toFixed(0)}%
                </p>
                <p className="text-sm text-muted-foreground">Approval Rate</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Hours by Project
            </CardTitle>
          </CardHeader>
          <CardContent>
            {hoursLoading || !chartsReady ? (
              <Skeleton className="h-[200px]" />
            ) : !hoursSummary?.by_project?.length ? (
              <div className="h-[200px] flex items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            ) : (
              <div className="h-[200px]" style={{ minWidth: 0 }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={200}>
                  <BarChart
                    data={hoursSummary.by_project.map((p) => ({
                      name: p.project_name,
                      hours: parseFloat(p.total_hours),
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 12, fill: '#64748b' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 12, fill: '#64748b' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '12px',
                      }}
                      formatter={(value) => [`${Number(value).toFixed(1)}h`, 'Hours']}
                    />
                    <Bar dataKey="hours" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
