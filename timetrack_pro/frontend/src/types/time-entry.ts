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
  created_at: string
  updated_at: string
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
