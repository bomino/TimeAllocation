import { Link } from 'react-router-dom'
import { FileText, ArrowRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'
import type { TimesheetListItem } from '@/types/timesheet'
import type { TimesheetStatus } from '@/lib/constants'

interface RecentTimesheetsProps {
  timesheets: TimesheetListItem[]
}

const statusVariant: Record<TimesheetStatus, 'draft' | 'submitted' | 'approved' | 'rejected'> = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
}

export function RecentTimesheets({ timesheets }: RecentTimesheetsProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">Recent Timesheets</CardTitle>
        <Link to="/timesheets">
          <Button variant="ghost" size="sm">
            View all
            <ArrowRight className="ml-1 h-4 w-4" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {timesheets.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FileText className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">No timesheets yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {timesheets.map((timesheet) => (
              <Link
                key={timesheet.id}
                to={`/timesheets/${timesheet.id}`}
                className="flex items-center justify-between rounded-md border p-3 hover:bg-accent transition-colors"
              >
                <div>
                  <p className="text-sm font-medium">
                    Week of {formatDate(timesheet.week_start)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {timesheet.total_hours} hours
                  </p>
                </div>
                <Badge variant={statusVariant[timesheet.status]}>
                  {timesheet.status.toLowerCase()}
                </Badge>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
