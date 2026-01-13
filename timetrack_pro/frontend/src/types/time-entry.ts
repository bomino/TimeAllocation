export interface TimeEntry {
  id: number
  user: {
    id: number
    email: string
  }
  project: {
    id: number
    name: string
  }
  timesheet: number | null
  date: string
  hours: string
  description: string
  billing_rate: string
  rate_source: string
  is_timer_entry: boolean
  timer_started_at: string | null
  timer_stopped_at: string | null
  elapsed_hours?: string
  created_at: string
  updated_at: string
}

export interface Timer {
  id: number
  project: {
    id: number
    name: string
  }
  description: string
  timer_started_at: string
  elapsed_hours: string
}

export interface CreateTimeEntryRequest {
  project: number
  date: string
  hours: number
  description?: string
}

export interface UpdateTimeEntryRequest {
  project?: number
  date?: string
  hours?: number
  description?: string
}

export interface StartTimerRequest {
  project: number
  description?: string
}

export interface StopTimerRequest {
  description?: string
}
