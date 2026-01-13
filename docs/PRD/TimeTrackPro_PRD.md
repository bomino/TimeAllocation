# Product Requirements Document (PRD)

## TimeTrack Pro - Employee Time Allocation Tracker

---

## 1. Executive Summary

**Product Name:** TimeTrack Pro
**Version:** 1.0
**Document Owner:** [Your Name/Company]
**Last Updated:** January 2026
**Target Audience:** Small businesses and teams with 5-50 employees

### Overview

TimeTrack Pro is a web-based employee time allocation and timesheet management system designed for small businesses that need **accurate billing, managerial oversight, and audit-ready records** without intrusive monitoring or unnecessary complexity. Employees can quickly log time across projects and tasks, while managers gain real-time visibility into utilization, approvals, and project costs.

---

## 2. Problem Statement

Small businesses need a straightforward way to:

- Track employee time allocation across multiple projects/clients
- Generate accurate billing reports for client work
- Identify productivity bottlenecks and resource allocation issues
- Maintain historical records for payroll and invoicing
- Provide transparency to employees about their time usage

### Current Pain Points

- Manual time tracking via spreadsheets is error-prone
- Lack of real-time visibility into project time allocation
- Difficult to generate accurate client billing reports
- No centralized system for time approval workflows
- Limited ability to analyze productivity trends
- Weak approval and audit processes

---

## 3. Goals and Objectives

### Primary Goals

1. **Simplify Time Entry:** Employees can log time in under 30 seconds
2. **Increase Accuracy:** Reduce time tracking errors by 80%
3. **Enable Billing:** Generate client-ready timesheets automatically
4. **Provide Insights:** Real-time dashboards for managers
5. **Ensure Compliance:** Maintain audit trails for all time entries

### Success Metrics

| Metric | Target |
|--------|--------|
| Employee adoption within 30 days | 95% |
| Average time entry completion | <20 seconds |
| Timesheet dispute reduction | 90% |
| Manager dashboard access frequency | ≥3x per week |
| Billable hours capture rate | 100% |
| Manager approval turnaround | <24 hours |

---

## 4. User Personas

### Persona 1: Employee (Primary User)

- **Name:** Sarah, Junior Developer
- **Needs:** Quick time entry, see personal time allocation, submit timesheets
- **Pain Points:** Forgets to log time, unsure which project to charge to
- **Tech Comfort:** Moderate

### Persona 2: Manager/Team Lead

- **Name:** Mike, Project Manager
- **Needs:** Team time visibility, approve timesheets, track project budgets
- **Pain Points:** No visibility until end of week, manual approval process
- **Tech Comfort:** High

### Persona 3: Business Owner/Admin

- **Name:** Business Owner
- **Needs:** Company-wide analytics, billing reports, user management
- **Pain Points:** Can't track profitability by project, manual report generation
- **Tech Comfort:** High

---

## 5. Functional Requirements

### 5.1 User Authentication & Authorization

**FR-1.1:** User Registration and Login

- Email/password authentication
- Password reset via email
- "Remember me" functionality
- Session timeout after 8 hours of inactivity

**FR-1.2:** Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| Employee | Log time, view own entries, submit timesheets |
| Manager | Employee permissions + approve team timesheets, view team reports |
| Admin | All permissions + user management, system configuration, rate management |

**FR-1.3:** User Profile Management

- Edit name, email, phone
- Upload profile photo
- Set default hourly rate (admin only)
- Set timezone preferences

---

### 5.2 Time Entry & Tracking

**FR-2.1:** Create Time Entry

Required Fields:

| Field | Type | Constraints |
|-------|------|-------------|
| Date | Date | Default to today, no future dates |
| Project/Client | Dropdown | Active projects only |
| Task/Category | Dropdown | Filtered by project |
| Hours | Decimal | e.g., 1.5, max 24/day |
| Description | Text | 500 char max |

Optional Fields:

- Tags (multi-select)
- Billable/Non-billable toggle
- Location (if relevant)

**FR-2.2:** Quick Time Entry (Timer-Based)

- Start/stop timer for active task
- Running timer visible on all pages
- One-click to switch between recent projects
- Suggested tasks based on history
- Persistent timer across page navigation

**FR-2.3:** Bulk Time Entry

- Weekly calendar view for batch entry
- Copy previous week's entries
- Copy specific day's entries
- Import from CSV template

**FR-2.4:** Edit/Delete Time Entries

- Edit any unsubmitted entry
- Delete own entries (with confirmation)
- Edit history/audit log (who changed what, when)
- Managers can edit/delete submitted entries with reason

**FR-2.5:** Time Entry Validation

| Rule | Behavior |
|------|----------|
| Daily limit | Cannot log more than 24 hours per day |
| Future dates | Cannot log future dates beyond today |
| Overlapping timers | Cannot submit overlapping timer entries |
| Excessive hours | Warning if daily total exceeds 12 hours |
| Required fields | Clear error messages for missing fields |
| Zero-hour timesheets | Cannot submit timesheets with zero total hours |
| Archived projects | Cannot log time to archived projects |

---

### 5.3 Projects & Task Management

**FR-3.1:** Project Management (Admin/Manager)

- Create/edit/archive projects

Project Fields:

| Field | Type | Required |
|-------|------|----------|
| Project name | Text | Yes |
| Client/customer name | Text | Yes |
| Project code | Text | Yes (unique) |
| Budget (hours) | Number | No |
| Budget (dollars) | Currency | No |
| Start date | Date | No |
| End date | Date | No |
| Project manager | User reference | Yes |
| Status | Enum | Yes (Active, On Hold, Completed, Archived) |
| Billing rate | Currency | No (uses default if empty) |

**FR-3.2:** Task/Category Management

- Create task categories per project
- Standard task library (Meeting, Development, Research, Admin, etc.)
- Task billing settings (billable/non-billable default)
- Associate tasks with specific projects

**FR-3.3:** Team Assignment

- Assign employees to projects
- Set employee-specific billing rates per project
- Define employee roles on projects

---

### 5.4 Timesheet Submission & Approval

**FR-4.1:** Timesheet Periods

- Weekly timesheets (Monday-Sunday)
- Automatic timesheet generation
- Lock previous periods after approval

**FR-4.2:** Submission Workflow

```
Employee submits weekly timesheet
         ↓
Manager receives notification
         ↓
Manager reviews and approves/rejects
         ↓
Employee receives approval/rejection notification
         ↓
Rejected timesheets require resubmission with corrections
```

**FR-4.3:** Approval Interface

- Manager sees all pending timesheets
- Side-by-side view of time entries
- Add comments/feedback
- Bulk approve multiple employees
- Filter by employee, date, status
- **No partial approvals** - approve/reject full timesheets only

---

### 5.5 Reporting & Analytics

**FR-5.1:** Employee Dashboard

- Current week summary (hours by project)
- Pending timesheet status
- Recent time entries (last 10)
- Quick stats: Total hours this month, billable %

**FR-5.2:** Manager Dashboard

- Team time allocation (current week/month)
- Project budget utilization
- Pending approvals count
- Top projects by hours
- Team utilization rate
- Overtime alerts

**FR-5.3:** Standard Reports

| Report | Description |
|--------|-------------|
| Time by Project | Total hours per project with date filters |
| Time by Employee | Individual employee breakdown |
| Billable vs Non-billable | Percentage and totals |
| Client Billing Report | Ready-to-invoice format with rates |
| Project Budget Report | Hours spent vs budget |
| Daily/Weekly/Monthly Summaries | Aggregate views |

Export Options: PDF, Excel, CSV

**FR-5.4:** Custom Report Builder (Phase 2)

- Select dimensions (employee, project, task, date range)
- Choose metrics (hours, cost, billable %)
- Save custom reports
- Schedule automated email delivery

**FR-5.5:** Performance Constraints

- Pre-aggregated summaries for common queries
- Custom reports limited to 24 months and 4 dimensions maximum

---

### 5.6 Notifications & Reminders

**FR-6.1:** Email Notifications

| Trigger | Timing | Configurable |
|---------|--------|--------------|
| No time logged today | Daily reminder | Yes |
| Timesheet submission reminder | Friday 4pm | Yes |
| Timesheet approved | Immediate | No |
| Timesheet rejected | Immediate | No |
| Weekly summary | Monday morning | Yes |

**FR-6.2:** In-App Notifications

- Real-time notification center
- Unread notification badge
- Mark as read/unread
- Clear all notifications

---

### 5.7 Administrative Functions

**FR-7.1:** User Management

- Add/remove users
- Assign roles
- Deactivate users (retain data, block login and project assignment)
- Bulk user import via CSV
- Reset user passwords

**FR-7.2:** Company Settings

| Setting | Options |
|---------|---------|
| Company name and logo | Text/Image |
| Billing currency | USD, EUR, GBP, etc. |
| Default work week | Hours (e.g., 40) |
| Fiscal year start | Month |
| Time rounding rules | Nearest 15min, 30min, etc. |
| Approval workflow settings | Various |
| Default billing rate | Currency |

**FR-7.3:** Audit Logging

- Track all user actions (login, time entry, edits, deletions)
- Export audit logs
- Retention period: 2 years minimum

---

## 6. Business Rules & Edge Cases

### 6.1 Time Entry Rules

| Rule | Enforcement |
|------|-------------|
| Zero-hour timesheets | Cannot be submitted |
| Inactive projects | Block new entries, retain history |
| Archived projects | Block new entries, retain history |
| Deactivated users | Retain historical data, block new actions |

### 6.2 Approval Rules

| Rule | Behavior |
|------|----------|
| Partial approvals | Not allowed - full timesheet only |
| Approved timesheets | Lock all associated time entries |
| Rejection | Requires comment from manager |

### 6.3 User Deactivation

- Historical data retained indefinitely
- Cannot log new time
- Cannot be assigned to projects
- Login blocked
- Reports still include historical data

---

## 7. Rate & Billing Logic

### 7.1 Rate Hierarchy

Rates are determined in the following priority order (highest to lowest):

| Priority | Rate Type | Description |
|----------|-----------|-------------|
| 1 | Employee-Project Rate | Specific rate for employee on specific project |
| 2 | Project Default Rate | Default rate for the project |
| 3 | Employee Default Rate | Employee's standard hourly rate |
| 4 | Company Default Rate | Fallback company-wide rate |

### 7.2 Rate Immutability

**Critical Rule:** Rates are **snapshotted at time entry creation**.

- When a time entry is created, the effective rate is calculated and stored
- No retroactive changes to submitted or approved entries
- Rate changes only affect future time entries
- Historical billing reports remain accurate

### 7.3 Billable Overrides

| User Role | Override Capability |
|-----------|---------------------|
| Employee | Toggle billable/non-billable (unless restricted by project) |
| Manager | Override any entry, changes logged in audit |
| Admin | Full override capability, changes logged in audit |

---

## 8. Timesheet Locking & Admin Overrides

### 8.1 Automatic Locking

- Approved timesheets are **automatically locked**
- Locked timesheets cannot be edited by employees or managers
- All associated time entries are locked with the timesheet

### 8.2 Admin Unlock Conditions

Admins may unlock a timesheet **only** for:

| Reason | Justification Required |
|--------|------------------------|
| Billing correction | Yes - describe the error |
| Compliance requirement | Yes - reference regulation/audit |
| Audit response | Yes - reference audit request |

### 8.3 Override Audit Trail

All admin overrides require:

- Written justification (stored permanently)
- Timestamp of action
- Previous state snapshot (JSON)
- Admin user identification

---

## 9. Non-Functional Requirements

### 9.1 Performance

| Metric | Target |
|--------|--------|
| Page load time | <2 seconds |
| Time entry submission | <1 second |
| Concurrent users | 50 minimum |
| Report generation (12 months) | <5 seconds |
| Database queries | Optimized with proper indexing |

### 9.2 Scalability

- Architecture supports growth to 200+ users
- Database can handle 1M+ time entries
- Horizontal scaling capability

### 9.3 Availability

| Metric | Target |
|--------|--------|
| Uptime (business hours 6am-8pm) | 99.5% |
| Scheduled maintenance window | Sundays 2am-4am |
| Database backups | Daily at midnight |
| Backup retention | 30 days |

### 9.4 Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

### 9.5 Accessibility

- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatible
- Color contrast requirements met

### 9.6 Mobile UX

- Log time in ≤3 taps
- Start/stop timer from any screen
- Responsive web only (no offline support in v1)
- Touch-friendly controls

---

## 10. Technical Requirements

### 10.1 Tech Stack

**Frontend:**

- React 18+ with TypeScript
- Tailwind CSS for styling
- Recharts for visualizations
- React Query for server state management

**Backend:**

- Django 5.x with Django REST Framework
- django-rest-framework-simplejwt for JWT authentication
- django-filter for query filtering
- Celery + Redis for background tasks (email notifications, report generation)
- drf-spectacular for OpenAPI documentation

**Database:**

- PostgreSQL 15+ (primary database)
- Redis (caching, session storage, Celery broker)

**Hosting:**

- Cloud platform: AWS, Google Cloud, or DigitalOcean
- Docker containerization
- CI/CD pipeline (GitHub Actions or GitLab CI)
- Gunicorn + Nginx for production serving

**Additional Tools:**

- Email service: SendGrid or AWS SES (via django-anymail)
- File storage: AWS S3 (via django-storages)
- Monitoring: Sentry for error tracking
- Testing: pytest-django, factory_boy for test fixtures

---

### 10.2 API Specification

#### Authentication

```
POST   /api/auth/login              # User login
POST   /api/auth/logout             # User logout
POST   /api/auth/register           # User registration
POST   /api/auth/password-reset     # Request password reset
POST   /api/auth/password-reset/:token  # Complete password reset
POST   /api/auth/refresh            # Refresh JWT token
DELETE /api/auth/sessions           # Revoke all sessions
```

#### Users

```
GET    /api/users                   # List users (admin)
GET    /api/users/:id               # Get user details
POST   /api/users                   # Create user (admin)
PUT    /api/users/:id               # Update user
DELETE /api/users/:id               # Deactivate user (admin)
GET    /api/users/me                # Current user profile
PUT    /api/users/me                # Update current user profile
```

#### Time Entries

```
GET    /api/time-entries            # List entries (with filters: date, project, user)
GET    /api/time-entries/:id        # Get single entry
POST   /api/time-entries            # Create entry
PUT    /api/time-entries/:id        # Update entry
DELETE /api/time-entries/:id        # Delete entry
POST   /api/time-entries/bulk       # Bulk create entries
POST   /api/time-entries/timer/start    # Start timer
POST   /api/time-entries/timer/stop     # Stop timer
GET    /api/time-entries/timer/active   # Get active timer
```

#### Projects

```
GET    /api/projects                # List projects
GET    /api/projects/:id            # Get project details
POST   /api/projects                # Create project (admin/manager)
PUT    /api/projects/:id            # Update project
DELETE /api/projects/:id            # Archive project
GET    /api/projects/:id/members    # List project members
POST   /api/projects/:id/members    # Add member to project
DELETE /api/projects/:id/members/:userId  # Remove member
```

#### Tasks

```
GET    /api/tasks                   # List all tasks
GET    /api/projects/:id/tasks      # List tasks for project
POST   /api/tasks                   # Create task
PUT    /api/tasks/:id               # Update task
DELETE /api/tasks/:id               # Delete task
```

#### Timesheets

```
GET    /api/timesheets              # List timesheets (with filters: user, period, status)
GET    /api/timesheets/:id          # Get timesheet details
POST   /api/timesheets/:id/submit   # Submit timesheet
POST   /api/timesheets/:id/approve  # Approve timesheet (manager)
POST   /api/timesheets/:id/reject   # Reject timesheet (manager)
POST   /api/timesheets/:id/unlock   # Unlock timesheet (admin only)
```

#### Rates

```
GET    /api/rates                   # List all rate configurations
GET    /api/rates/effective/:userId/:projectId  # Get effective rate for user/project
POST   /api/rates                   # Create rate override
PUT    /api/rates/:id               # Update rate
DELETE /api/rates/:id               # Remove rate override
```

#### Reports

```
GET    /api/reports/time-by-project     # Time aggregated by project
GET    /api/reports/time-by-employee    # Time aggregated by employee
GET    /api/reports/billable-summary    # Billable vs non-billable breakdown
GET    /api/reports/budget-utilization  # Project budget status
POST   /api/reports/export              # Export report (returns PDF/CSV)
```

#### Admin & Audit

```
GET    /api/audit/logs              # List audit logs (admin)
GET    /api/audit/overrides         # List admin override actions
GET    /api/settings                # Get company settings
PUT    /api/settings                # Update company settings (admin)
```

#### Data Import

```
POST   /api/import/users            # Bulk import users via CSV
POST   /api/import/projects         # Bulk import projects
POST   /api/import/time-entries     # Bulk import historical entries
GET    /api/import/template/:type   # Download CSV template (users, projects, time-entries)
POST   /api/import/validate         # Validate import file before processing
```

---

### 10.3 Database Schema

#### Users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('employee', 'manager', 'admin')),
    hourly_rate DECIMAL(10,2),
    timezone VARCHAR(50) DEFAULT 'UTC',
    profile_photo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Projects

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) UNIQUE NOT NULL,
    budget_hours DECIMAL(10,2),
    budget_amount DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'on_hold', 'completed', 'archived')),
    manager_id INTEGER REFERENCES users(id),
    default_billing_rate DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tasks

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    project_id INTEGER REFERENCES projects(id),
    is_billable BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Time Entries

```sql
CREATE TABLE time_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    project_id INTEGER REFERENCES projects(id) NOT NULL,
    task_id INTEGER REFERENCES tasks(id),
    date DATE NOT NULL,
    hours DECIMAL(5,2) NOT NULL CHECK (hours > 0 AND hours <= 24),
    description TEXT,
    is_billable BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    -- Rate snapshot (immutable after creation)
    billing_rate DECIMAL(10,2) NOT NULL,
    rate_source VARCHAR(30) NOT NULL CHECK (rate_source IN ('employee_project', 'project', 'employee', 'company')),
    rate_id INTEGER REFERENCES rates(id),
    -- Timer fields
    timer_started_at TIMESTAMP,
    timer_stopped_at TIMESTAMP,
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT valid_date CHECK (date <= CURRENT_DATE)
);

CREATE INDEX idx_time_entries_user_date ON time_entries(user_id, date);
CREATE INDEX idx_time_entries_project ON time_entries(project_id);
CREATE INDEX idx_time_entries_status ON time_entries(status);
```

#### Timesheets

```sql
CREATE TABLE timesheets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    submitted_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    notes TEXT,
    -- Locking fields
    locked_at TIMESTAMP,
    locked_by INTEGER REFERENCES users(id),
    unlock_reason TEXT,
    unlocked_at TIMESTAMP,
    unlocked_by INTEGER REFERENCES users(id),
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    UNIQUE(user_id, period_start, period_end)
);
```

#### Rates

```sql
CREATE TABLE rates (
    id SERIAL PRIMARY KEY,
    type VARCHAR(30) NOT NULL CHECK (type IN ('company', 'employee', 'project', 'employee_project')),
    employee_id INTEGER REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    hourly_rate DECIMAL(10,2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by INTEGER REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraints for type validation
    CONSTRAINT valid_employee_rate CHECK (
        (type = 'employee' AND employee_id IS NOT NULL AND project_id IS NULL) OR
        (type = 'project' AND project_id IS NOT NULL AND employee_id IS NULL) OR
        (type = 'employee_project' AND employee_id IS NOT NULL AND project_id IS NOT NULL) OR
        (type = 'company' AND employee_id IS NULL AND project_id IS NULL)
    )
);

CREATE INDEX idx_rates_employee ON rates(employee_id);
CREATE INDEX idx_rates_project ON rates(project_id);
CREATE INDEX idx_rates_effective ON rates(effective_from, effective_to);
```

#### Project Members

```sql
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    role VARCHAR(50),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);
```

#### Audit Log

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_date ON audit_log(created_at);
```

#### Admin Overrides

```sql
CREATE TABLE admin_overrides (
    id SERIAL PRIMARY KEY,
    timesheet_id INTEGER REFERENCES timesheets(id) NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('unlock', 'edit', 'delete')),
    reason TEXT NOT NULL,
    performed_by INTEGER REFERENCES users(id) NOT NULL,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    previous_state JSONB NOT NULL
);

CREATE INDEX idx_admin_overrides_timesheet ON admin_overrides(timesheet_id);
```

#### Notifications

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
```

#### Company Settings

```sql
CREATE TABLE company_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 10.4 API Response Standards

#### Success Response

```json
{
    "success": true,
    "data": {
        "id": 123,
        "name": "Example Project"
    },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "total_pages": 5
    }
}
```

#### Error Response

```json
{
    "success": false,
    "error": {
        "code": "VAL_001",
        "message": "Validation failed",
        "details": [
            {
                "field": "hours",
                "message": "Hours cannot exceed 24 per day"
            },
            {
                "field": "project_id",
                "message": "Project is archived and cannot accept new entries"
            }
        ]
    }
}
```

#### Pagination Parameters

| Parameter | Default | Max | Description |
|-----------|---------|-----|-------------|
| page | 1 | - | Page number |
| per_page | 20 | 100 | Items per page |
| sort | varies | - | Sort field |
| order | asc | - | Sort order (asc/desc) |

---

### 10.5 Error Handling Standards

#### Error Code Categories

| Prefix | Category | HTTP Status |
|--------|----------|-------------|
| AUTH | Authentication/Authorization | 401, 403 |
| VAL | Validation | 400 |
| BIZ | Business Logic | 409, 422 |
| NOT | Not Found | 404 |
| SYS | System/Server | 500, 503 |

#### Error Code Reference

**Authentication Errors (AUTH)**

| Code | Message | Description |
|------|---------|-------------|
| AUTH_001 | Invalid credentials | Wrong email or password |
| AUTH_002 | Session expired | JWT token expired |
| AUTH_003 | Insufficient permissions | User lacks required role |
| AUTH_004 | Account locked | Too many failed attempts |
| AUTH_005 | Account deactivated | User account is disabled |

**Validation Errors (VAL)**

| Code | Message | Description |
|------|---------|-------------|
| VAL_001 | Required field missing | Mandatory field not provided |
| VAL_002 | Invalid format | Field format incorrect |
| VAL_003 | Value out of range | Value exceeds allowed limits |
| VAL_004 | Duplicate entry | Unique constraint violated |
| VAL_005 | Invalid reference | Foreign key doesn't exist |

**Business Logic Errors (BIZ)**

| Code | Message | Description |
|------|---------|-------------|
| BIZ_001 | Cannot modify locked timesheet | Timesheet is approved/locked |
| BIZ_002 | Cannot log time to archived project | Project status is archived |
| BIZ_003 | Cannot exceed 24 hours per day | Daily hour limit exceeded |
| BIZ_004 | Cannot submit empty timesheet | No time entries in period |
| BIZ_005 | Cannot approve own timesheet | Self-approval not permitted |
| BIZ_006 | Overlapping timer entry | Timer conflicts with existing entry |
| BIZ_007 | Future date not allowed | Cannot log time for future dates |

**Not Found Errors (NOT)**

| Code | Message | Description |
|------|---------|-------------|
| NOT_001 | Resource not found | Requested entity doesn't exist |
| NOT_002 | User not found | User ID invalid |
| NOT_003 | Project not found | Project ID invalid |

**System Errors (SYS)**

| Code | Message | Description |
|------|---------|-------------|
| SYS_001 | Database error | Database operation failed |
| SYS_002 | External service unavailable | Third-party API down |
| SYS_003 | Rate limit exceeded | Too many requests |

---

## 11. UI/UX Requirements

### 11.1 Navigation Structure

**Main Navigation (Sidebar/Top Nav):**

| Menu Item | Visible To |
|-----------|------------|
| Dashboard | All |
| Time Entry | All |
| My Time | All |
| Timesheets | All |
| Reports | Manager, Admin |
| Projects | Manager, Admin |
| Team | Manager |
| Settings | Admin |

### 11.2 Key Screens

#### Dashboard (Employee View)

```
┌─────────────────────────────────────────────┐
│ Welcome back, Sarah!                         │
│                                              │
│ ┌──────────────┐  ┌──────────────┐          │
│ │ This Week    │  │ Pending      │          │
│ │ 32.5 hours   │  │ Timesheet    │          │
│ │ 85% billable │  │ Submit Now → │          │
│ └──────────────┘  └──────────────┘          │
│                                              │
│ Recent Time Entries:                         │
│ ┌────────────────────────────────────────┐  │
│ │ Jan 13 | Project A | Development | 4h │  │
│ │ Jan 12 | Project B | Meeting     | 2h │  │
│ │ Jan 12 | Project A | Code Review | 1.5h│  │
│ └────────────────────────────────────────┘  │
│                                              │
│ ┌─────────────────────────────────────────┐ │
│ │ [+ Log Time]                             │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

#### Time Entry Form (Modal/Page)

```
┌─────────────────────────────────────────┐
│ Log Time                          [X]    │
├─────────────────────────────────────────┤
│ Date:         [Jan 13, 2026 ▼]          │
│ Project:      [Select Project... ▼]     │
│ Task:         [Select Task... ▼]        │
│ Hours:        [____]                     │
│ Billable:     [✓] Yes  [ ] No           │
│ Description:                             │
│ ┌───────────────────────────────────┐   │
│ │                                   │   │
│ │                                   │   │
│ └───────────────────────────────────┘   │
│                                          │
│        [Cancel]  [Save Time Entry]      │
└─────────────────────────────────────────┘
```

#### Weekly Calendar View

```
Week of Jan 13-19, 2026        Total: 32.5 hrs

Mon 13  [+]  ████████ 8h
Tue 14  [+]  ██████ 6h
Wed 15  [+]  ████████ 8h
Thu 16  [+]  ██████████ 10h
Fri 17  [+]  █ 0.5h
Sat 18  [+]
Sun 19  [+]

[< Previous Week]  [Submit Timesheet]  [Next Week >]
```

### 11.3 Design Guidelines

| Element | Specification |
|---------|---------------|
| Color Scheme | Professional (blue/gray primary, green for success, red for errors) |
| Typography | Clear, readable fonts (16px minimum body text) |
| Spacing | Generous whitespace, 8px grid system |
| Buttons | Primary actions prominent, secondary actions subtle |
| Forms | Inline validation, clear error messages |
| Loading States | Skeleton screens or spinners |
| Empty States | Helpful messaging + call-to-action |

### 11.4 Mobile UX Requirements

| Requirement | Specification |
|-------------|---------------|
| Time entry | ≤3 taps to complete |
| Timer access | Available from any screen |
| Responsiveness | Fully responsive (320px - 1920px) |
| Touch targets | Minimum 44x44px |
| Offline | Not supported in v1 |

---

## 12. Security and Compliance

### 12.1 Authentication Security

- Passwords hashed with bcrypt (cost factor 12+)
- No plain text password storage
- Password reset tokens expire in 1 hour
- Email verification for new accounts (optional)

### 12.2 Password Requirements

**Minimum Requirements:**

| Requirement | Specification |
|-------------|---------------|
| Length | 8+ characters |
| Complexity | At least 3 of 4 categories |
| - Uppercase | A-Z |
| - Lowercase | a-z |
| - Numbers | 0-9 |
| - Special | !@#$%^&*()_+-=[]{}|;:,.<>? |
| Blocklist | Not in common password list (top 10,000) |
| Personal info | Cannot contain username or email |
| History | Cannot reuse last 5 passwords |

**Password Reset:**

| Setting | Value |
|---------|-------|
| Token expiry | 1 hour |
| Token usage | Single use only |
| Session impact | Invalidates all existing sessions |

### 12.3 Session Management

**Session Configuration:**

| Setting | Value |
|---------|-------|
| JWT expiry | 8 hours |
| Refresh token expiry | 7 days |
| Concurrent sessions | Max 3 per user |
| Password change | Automatic logout of all sessions |
| Session revocation | API available for admin |

**Security Headers:**

| Header | Value |
|--------|-------|
| Secure | true (HTTPS only) |
| HttpOnly | true (no JS access) |
| SameSite | Strict |
| CSRF | Token validation on all mutations |

### 12.4 Authorization Controls

- Check permissions on every API request
- No client-side only authorization
- Database-level foreign key constraints
- Row-level security where applicable
- All authorization failures logged

### 12.5 Data Security

| Measure | Implementation |
|---------|----------------|
| Transport | HTTPS/TLS 1.2+ for all traffic |
| SQL Injection | Parameterized queries only |
| XSS | Input sanitization, output encoding |
| CSRF | Token validation on all forms |
| Rate Limiting | 100 requests/minute per user, 5 login attempts then 15-min lockout |
| Dependency Scanning | Automated vulnerability checks |

### 12.6 Compliance

| Requirement | Implementation |
|-------------|----------------|
| GDPR | Data export, deletion on request, consent tracking |
| CCPA | Similar to GDPR for California users |
| Data Retention | Documented policy, minimum 2 years for audit logs |
| Terms of Service | Required acknowledgment |
| Privacy Policy | Required acknowledgment |
| Cookie Consent | If analytics tracking enabled |

---

## 13. Data Migration & Onboarding

### 13.1 CSV Import Support

| Data Type | Template Available | Fields |
|-----------|-------------------|--------|
| Users | Yes | email, first_name, last_name, role, hourly_rate |
| Projects | Yes | name, client_name, project_code, budget_hours, status |
| Time Entries | Yes | user_email, project_code, date, hours, description, is_billable |

### 13.2 Admin Onboarding Wizard

1. Company profile setup (name, logo, timezone)
2. Default settings configuration (work week, billing currency)
3. First admin user creation
4. Optional: bulk user import
5. Optional: project creation
6. Guided tour of key features

### 13.3 Data Validation

- Pre-import validation with detailed error report
- Dry-run mode to preview changes
- Rollback capability for failed imports
- Duplicate detection and handling options

---

## 14. Competitive Positioning

### 14.1 Core Philosophy

TimeTrack Pro prioritizes **clarity, approvals, and billing accuracy** over surveillance. It is built for **trust-based teams** that need reliable records, not micromanagement tools.

### 14.2 What We Are NOT

| Feature | Status | Reason |
|---------|--------|--------|
| GPS tracking | Not included | Trust-based philosophy |
| Screenshot monitoring | Not included | Trust-based philosophy |
| Keystroke logging | Not included | Trust-based philosophy |
| Activity monitoring | Not included | Trust-based philosophy |

### 14.3 Differentiators

- **Simple:** Time entry in <30 seconds
- **Transparent:** Clear approval workflows
- **Accurate:** Rate snapshotting prevents billing disputes
- **Auditable:** Complete history for compliance
- **Respectful:** No invasive monitoring

---

## 15. Pricing & Monetization

### 15.1 Pricing Model

Per-user, per-month subscription

### 15.2 Planned Tiers

| Tier | Target | Key Features |
|------|--------|--------------|
| Starter | 5-10 users | Core time tracking, basic reports |
| Growth | 11-30 users | + Manager dashboards, approvals, integrations |
| Pro | 31-50 users | + Custom reports, API access, priority support |

*Exact pricing to be determined post-MVP validation*

---

## 16. Success Metrics & KPIs

### 16.1 Launch Metrics (First 30 Days)

| Metric | Target |
|--------|--------|
| User activation rate | 95% |
| Daily active users | 80% |
| Average time entries per user per day | 3+ |
| Timesheet submission rate | 90% |
| Manager approval turnaround | <24 hours |

### 16.2 Ongoing Metrics

| Metric | Target |
|--------|--------|
| User satisfaction score | 4+/5 |
| Time to log entry | <30 seconds |
| System uptime | 99.5% |
| Mobile usage | 40%+ |
| Report generation frequency (managers) | 3x/week |

---

## 17. Development Phases

### Phase 1: MVP

**Focus:** Core time tracking and approval workflow

**Features:**

- User authentication (login/register/password reset)
- Basic time entry (manual entry form)
- Simple project/task management
- Weekly timesheet view
- Employee dashboard
- Basic approval workflow
- Time by project report

**Deliverable:** Working app for employees to log time and managers to approve

---

### Phase 2: Enhanced Features

**Focus:** Productivity and analytics

**Features:**

- Timer functionality (start/stop)
- Bulk time entry
- Manager dashboard with analytics
- Enhanced reporting (billable summary, budget tracking)
- Email notifications
- Audit logging
- Mobile responsive optimization
- Rate management system

**Deliverable:** Feature-complete system with analytics

---

### Phase 3: Polish & Scale

**Focus:** Production readiness

**Features:**

- Custom report builder
- Advanced filtering and search
- Performance optimization
- Security hardening
- User documentation
- Admin training materials
- Beta testing with employees
- Data import/export tools

**Deliverable:** Production-ready system

---

### Phase 4: Post-Launch

**Focus:** Expansion and integrations

**Features:**

- User feedback integration
- Integration with payroll systems
- Integration with project management tools (Jira, Asana)
- Mobile native apps (iOS/Android)
- API for third-party integrations
- Advanced analytics and AI insights

---

## 18. Out of Scope (v1.0)

The following features are NOT included in v1.0:

| Feature | Status | Future Phase |
|---------|--------|--------------|
| Geolocation tracking/GPS | Not planned | - |
| Screenshot monitoring | Not planned | - |
| Automatic time tracking (app usage) | Not planned | - |
| Slack/Jira integrations | Phase 4 | 4 |
| Expense tracking | Future | TBD |
| Leave/PTO management | Future | TBD |
| Payroll processing | Future | TBD |
| Client portal access | Future | TBD |
| Native mobile apps | Phase 4 | 4 |
| Multi-currency support | Future | TBD |
| Advanced AI/ML features | Phase 4 | 4 |
| Offline support | Future | TBD |

---

## 19. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| Time Entry | Single record of time spent on a task |
| Timesheet | Collection of time entries for a specific period (usually weekly) |
| Billable Hours | Time that can be charged to a client |
| Non-billable | Internal time (admin, meetings, training) |
| Utilization Rate | Percentage of worked hours that are billable |
| Rate Snapshotting | Capturing billing rate at time entry creation |

### B. Sample User Flows

**Flow 1: Employee Logs Time**

1. Employee logs in
2. Clicks "Log Time" or timer icon
3. Selects project from dropdown (recently used appear first)
4. Selects task category
5. Enters hours (or starts/stops timer)
6. Adds brief description
7. Clicks "Save"
8. Time entry appears in "My Time" view
9. Repeats throughout the week

**Flow 2: Employee Submits Timesheet**

1. Employee navigates to "Timesheets"
2. Views current week summary
3. Reviews all entries for accuracy
4. Clicks "Submit Timesheet"
5. Confirmation message appears
6. Manager receives notification

**Flow 3: Manager Approves Timesheet**

1. Manager receives email notification
2. Logs in and navigates to "Pending Approvals"
3. Clicks on employee's timesheet
4. Reviews time entries
5. Adds comment if needed
6. Clicks "Approve" or "Reject"
7. Employee receives notification

**Flow 4: Admin Unlocks Timesheet**

1. Admin receives request to correct approved timesheet
2. Navigates to timesheet in admin view
3. Clicks "Unlock Timesheet"
4. Enters justification reason (required)
5. Confirms unlock action
6. Action logged in admin_overrides table
7. Employee can now make corrections
8. Timesheet re-submitted for approval

---

## 20. AI Assistant Development Instructions

When developing this application:

### 1. Start with MVP (Phase 1)

Focus on core functionality first:

- Authentication
- Time entry
- Timesheets
- Basic approval
- Simple reporting

### 2. Django Best Practices

**Project Structure:**

```
timetrack_pro/
├── config/                 # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── users/              # User management, auth
│   ├── projects/           # Projects, tasks
│   ├── timeentries/        # Time entries, timers
│   ├── timesheets/         # Timesheet submission/approval
│   ├── rates/              # Billing rate hierarchy
│   └── reports/            # Reporting, analytics
├── core/                   # Shared utilities, base models
└── manage.py
```

**API Design:**

- Use DRF ViewSets for CRUD operations
- Use `@action` decorator for custom endpoints (timer/start, timer/stop)
- Implement permission classes per role (IsEmployee, IsManager, IsAdmin)
- Use serializers for validation and rate snapshotting logic
- Leverage django-filter for query parameters

**Models:**

- Use `TimeStampedModel` base class for created_at/updated_at
- Implement rate calculation in model method or manager
- Use Django signals sparingly (prefer explicit calls)
- Add database indexes on foreign keys and frequently filtered fields

**Background Tasks (Celery):**

- Email notifications (timesheet submitted, approved, rejected)
- Report generation (PDF/Excel export)
- Daily reminder emails (missing time entries)
- Weekly timesheet submission reminders

### 3. Prioritize

1. **User experience:** Simple, intuitive interfaces
2. **Data integrity:** Proper validation and constraints
3. **Performance:** Optimize database queries with select_related/prefetch_related
4. **Security:** Protect against OWASP top 10

### 4. Create

- Django migrations (version controlled)
- OpenAPI docs via drf-spectacular
- README with setup instructions
- .env.example template
- pytest test suite with factory_boy fixtures
- Django management commands for seed data

### 5. Ask for Clarification On

- Hosting/deployment strategy
- Any ambiguous business rules
- Design preferences beyond requirements
- Integration priorities

---

**END OF PRD**
