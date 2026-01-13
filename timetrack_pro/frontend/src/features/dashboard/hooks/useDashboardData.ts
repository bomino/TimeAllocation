import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import type { TimesheetListItem } from '@/types/timesheet'
import type { TimeEntry } from '@/types/time-entry'
import { startOfWeek, endOfWeek, format, eachDayOfInterval } from 'date-fns'

interface DashboardData {
  weeklyHours: Array<{ day: string; hours: number }>
  totalHoursThisWeek: number
  recentTimesheets: TimesheetListItem[]
  pendingTimesheetsCount: number
}

export function useDashboardData() {
  return useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const now = new Date()
      const weekStart = startOfWeek(now, { weekStartsOn: 1 })
      const weekEnd = endOfWeek(now, { weekStartsOn: 1 })

      const [entriesResponse, timesheetsResponse] = await Promise.all([
        apiClient.get<{ success: boolean; data: TimeEntry[] }>('/time-entries/', {
          params: {
            date_from: format(weekStart, 'yyyy-MM-dd'),
            date_to: format(weekEnd, 'yyyy-MM-dd'),
          },
        }),
        apiClient.get<{ success: boolean; data: TimesheetListItem[] }>('/timesheets/', {
          params: { per_page: 5 },
        }),
      ])

      const entries = entriesResponse.data.data ?? []

      const timesheets = timesheetsResponse.data.data || []

      const daysOfWeek = eachDayOfInterval({ start: weekStart, end: weekEnd })
      const hoursByDay = new Map<string, number>()

      daysOfWeek.forEach((day) => {
        hoursByDay.set(format(day, 'yyyy-MM-dd'), 0)
      })

      let totalHours = 0
      entries.forEach((entry: TimeEntry) => {
        const dateKey = entry.date
        const hours = parseFloat(entry.hours)
        totalHours += hours
        if (hoursByDay.has(dateKey)) {
          hoursByDay.set(dateKey, (hoursByDay.get(dateKey) || 0) + hours)
        }
      })

      const weeklyHours = daysOfWeek.map((day) => ({
        day: format(day, 'EEE'),
        hours: Math.round((hoursByDay.get(format(day, 'yyyy-MM-dd')) || 0) * 10) / 10,
      }))

      const pendingTimesheetsCount = timesheets.filter(
        (t: TimesheetListItem) => t.status === 'SUBMITTED'
      ).length

      return {
        weeklyHours,
        totalHoursThisWeek: Math.round(totalHours * 10) / 10,
        recentTimesheets: timesheets.slice(0, 3),
        pendingTimesheetsCount,
      }
    },
  })
}
