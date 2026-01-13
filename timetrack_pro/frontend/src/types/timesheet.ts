import type { TimesheetStatus } from '@/lib/constants'
import type { TimeEntry } from './time-entry'

export interface TimesheetListItem {
  id: number
  user: {
    id: number
    email: string
    first_name: string
    last_name: string
  }
  week_start: string
  status: TimesheetStatus
  submitted_at: string | null
  approved_at: string | null
  approved_by: {
    id: number
    email: string
    first_name: string
    last_name: string
  } | null
  locked_at: string | null
  total_hours: string
  created_at: string
  updated_at: string
}

export interface TimesheetComment {
  id: number
  author: {
    id: number
    email: string
    first_name: string
    last_name: string
  }
  text: string
  entry_id: number | null
  resolved: boolean
  created_at: string
}

export interface Timesheet extends TimesheetListItem {
  entries: TimeEntry[]
  comments: TimesheetComment[]
}

export interface SubmitTimesheetRequest {
  id: number
}

export interface ApproveTimesheetRequest {
  id: number
}

export interface RejectTimesheetRequest {
  id: number
  comment: string
  entry_id?: number
}

export interface UnlockTimesheetRequest {
  id: number
  reason: string
}

export interface AddCommentRequest {
  timesheet_id: number
  text: string
  entry_id?: number
}
