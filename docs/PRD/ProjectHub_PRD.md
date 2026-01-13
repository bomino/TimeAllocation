# Product Requirements Document (PRD)

## ProjectHub - Project Management System

---

## 1. Executive Summary

**Product Name:** ProjectHub
**Version:** 1.0
**Document Owner:** [Your Name/Company]
**Last Updated:** January 2026
**Target Audience:** Small business teams (5-50 employees)

### Overview

ProjectHub is a comprehensive web-based project management platform that enables small business teams to plan, execute, and track projects from initiation to completion. The system provides multiple views (Kanban, List, Calendar, Gantt), collaboration tools, file management, and real-time progress tracking to keep teams aligned and productive.

### Integration with TimeTrack Pro

ProjectHub integrates seamlessly with TimeTrack Pro for comprehensive time tracking and billing. While ProjectHub handles project planning and task management, TimeTrack Pro provides detailed time allocation, billing rates, and timesheet workflows.

---

## 2. Problem Statement

Small businesses need a centralized platform to:

- Organize and track multiple projects simultaneously
- Break down projects into manageable tasks with clear ownership
- Visualize project timelines and dependencies
- Collaborate effectively across distributed teams
- Monitor progress and identify blockers in real-time
- Maintain project documentation and files in one place

### Current Pain Points

- Projects tracked across disconnected tools (email, spreadsheets, chat)
- Lack of visibility into project status and blockers
- Unclear task ownership and accountability
- Missed deadlines due to poor planning and tracking
- Difficulty prioritizing work across multiple projects
- Lost time searching for project files and documentation
- No historical data for estimating future projects

---

## 3. Goals and Objectives

### Primary Goals

1. **Centralize Work:** Single source of truth for all projects and tasks
2. **Improve Visibility:** Real-time status updates and progress tracking
3. **Enhance Collaboration:** Seamless team communication and file sharing
4. **Increase Delivery Rate:** Complete 90% of projects on time
5. **Reduce Context Switching:** All project information in one place

### Success Metrics

| Metric | Target |
|--------|--------|
| Team adoption within 45 days | 95% |
| Reduction in project overruns | 30% |
| Reduction in status update meetings | 50% |
| Tasks completed by due date | 80% |
| User satisfaction score | 4.5+/5 |
| Team productivity increase | 20% |

---

## 4. User Personas

### Persona 1: Project Manager

- **Name:** Lisa, Senior Project Manager
- **Needs:** Oversee multiple projects, track progress, manage resources, report to leadership
- **Pain Points:** Constantly chasing status updates, unclear resource availability, manual reporting
- **Tech Comfort:** High
- **Key Activities:** Create projects, assign tasks, monitor timelines, generate reports

### Persona 2: Team Member/Contributor

- **Name:** Alex, Marketing Specialist
- **Needs:** Clear task list, understand priorities, collaborate with teammates, track own work
- **Pain Points:** Unclear priorities, switching between tools, missed updates
- **Tech Comfort:** Moderate
- **Key Activities:** Complete tasks, update status, communicate with team, upload deliverables

### Persona 3: Team Lead/Department Head

- **Name:** Jordan, Engineering Lead
- **Needs:** Oversee team workload, track department initiatives, balance resources
- **Pain Points:** Team overload, competing priorities, lack of historical data
- **Tech Comfort:** High
- **Key Activities:** Review team capacity, prioritize work, mentor PMs, approve timelines

### Persona 4: Executive/Business Owner

- **Name:** Business Owner
- **Needs:** High-level portfolio view, strategic insights, ROI tracking
- **Pain Points:** No visibility into project health, can't predict delivery dates
- **Tech Comfort:** High
- **Key Activities:** Review portfolio dashboard, check project health, make strategic decisions

---

## 5. Functional Requirements

### 5.1 User Management & Authentication

**FR-1.1:** User Authentication

- Email/password login
- SSO support (Google, Microsoft) - Phase 2
- Password reset via email
- Two-factor authentication (optional, Phase 2)
- Session timeout after 8 hours of inactivity

**FR-1.2:** Role-Based Access Control

| Role | Permissions |
|------|-------------|
| Viewer | Read-only access to assigned projects |
| Member | Create/edit tasks, comment, upload files |
| Project Manager | All member permissions + create projects, manage team, reporting |
| Admin | All permissions + user management, workspace settings |

**FR-1.3:** User Profiles

- Name, email, phone, job title
- Profile photo
- Skills/expertise tags
- Timezone and language preferences
- Notification preferences
- Availability status (Available, Busy, Away, Off)

---

### 5.2 Workspace & Organization

**FR-2.1:** Workspace Management (Admin)

- Company/workspace name and logo
- Workspace settings and defaults
- Custom fields configuration
- Email domain restrictions
- Data retention policies

**FR-2.2:** Teams & Departments

- Create organizational teams (Engineering, Marketing, Sales, etc.)
- Assign users to teams
- Team-based project visibility
- Department-level dashboards

**FR-2.3:** Workspace Templates

- Pre-built project templates (Software Development, Marketing Campaign, Event Planning, etc.)
- Custom template creation
- Template library sharing

---

### 5.3 Project Management

**FR-3.1:** Create & Configure Projects

Required Fields:

| Field | Type | Constraints |
|-------|------|-------------|
| Project name | Text | 1-255 characters |
| Project key/code | Text | Auto-generated or custom, unique |
| Project owner/manager | User reference | Required |
| Start date | Date | Required |
| End date | Date | Must be >= start date |

Optional Fields:

- Description (rich text editor)
- Project status (Planning, Active, On Hold, Completed, Archived)
- Priority (Low, Medium, High, Critical)
- Budget (hours and/or dollars)
- Client/customer name
- Department/team assignment
- Tags/labels
- Custom fields

**FR-3.2:** Project Visibility & Access

| Visibility | Description |
|------------|-------------|
| Private | Invite only |
| Team-level | Visible to specific teams |
| Company-wide | All users can view |
| Guest | Limited permissions for external users |

**FR-3.3:** Project Settings

- Default task workflow
- Task number prefix
- Notification rules
- File storage limits
- Archive/delete options

**FR-3.4:** Project Dashboard (Per Project)

- Progress overview (% complete)
- Task status distribution
- Timeline view
- Key milestones
- Recent activity feed
- Team members list
- Quick stats (total tasks, overdue, completed this week)

---

### 5.4 Task Management

**FR-4.1:** Create Tasks/Issues

Required Fields:

| Field | Type | Constraints |
|-------|------|-------------|
| Task title | Text | 1-500 characters |
| Project assignment | Reference | Required |

Optional Fields:

| Field | Type | Description |
|-------|------|-------------|
| Description | Rich text | Formatting, images, links |
| Task type | Enum | Task, Bug, Feature, Epic, Story |
| Status | Enum | Per workflow (default: To Do, In Progress, Review, Done) |
| Priority | Enum | Low, Medium, High, Critical |
| Assignee(s) | User reference(s) | Single or multiple |
| Due date | Date | Optional deadline |
| Estimated time | Number | Hours or story points |
| Tags/labels | Multi-select | Categorization |
| Parent task | Reference | For subtasks |
| Dependencies | Reference(s) | Blocked by, blocks |
| Attachments | Files | Any supported type |
| Checklist items | Array | Sub-items within task |
| Custom fields | Various | Per workspace config |

**FR-4.2:** Task Relationships

- Parent-child hierarchy (tasks can have subtasks up to 3 levels)
- Task dependencies (must be completed before/after)
- Related tasks (loose association)
- Duplicate/clone tasks
- Visual dependency mapping

**FR-4.3:** Task Workflows

- Customizable status columns per project
- Drag-and-drop status changes
- Status transition rules (optional approvals)
- Automated status changes based on conditions
- Workflow templates (To Do → In Progress → Review → Done)

**FR-4.4:** Task Assignment & Ownership

- Assign to single user or multiple users
- Assign to entire team
- Unassigned task pool
- Reassignment with notification
- Task ownership transfer

**FR-4.5:** Task Updates & Activity

- Comment on tasks
- @mention users in comments
- Attach files to tasks
- Activity log (who did what, when)
- Watch/subscribe to tasks
- Task history/audit trail

**FR-4.6:** Bulk Task Operations

- Multi-select tasks
- Bulk status change
- Bulk assignee change
- Bulk move to different project
- Bulk delete (with confirmation)
- Bulk export to CSV/Excel

**FR-4.7:** Task Templates

- Create task templates with predefined fields
- Quick create from template
- Template library

---

### 5.5 Views & Visualization

**FR-5.1:** Multiple View Types

**List View:**

- Sortable, filterable task list
- Group by: Status, Assignee, Priority, Due Date, etc.
- Inline editing of key fields
- Expand/collapse task details
- Column customization

**Kanban Board View:**

- Customizable columns (by status)
- Drag-and-drop between columns
- WIP (Work In Progress) limits per column
- Swimlanes (by assignee, priority, etc.)
- Card customization (show/hide fields)
- Quick add task to column

**Calendar View:**

- Month/week/day views
- Tasks displayed by due date
- Drag-and-drop to reschedule
- Color-coded by project/priority
- Filter by project, assignee, tag
- Milestone markers

**Timeline/Gantt View:**

- Horizontal timeline with task bars
- Drag-and-drop to adjust dates
- Visual dependency lines
- Critical path highlighting
- Milestone markers
- Resource allocation view
- Zoom levels (day, week, month, quarter)
- Export to PDF

**Table View:**

- Spreadsheet-like interface
- All task fields visible/editable
- Sorting and filtering
- Column reordering
- Freeze columns
- Export to Excel/CSV

**FR-5.2:** View Customization

- Save custom views per user
- Share views with team
- Default view per project
- Quick switch between views
- Filter combinations saved

**FR-5.3:** Filtering & Search

- Filter by: Status, Assignee, Priority, Due Date, Tags, Custom Fields
- Combine multiple filters (AND/OR logic)
- Save filter presets
- Global search across all projects
- Advanced search with operators
- Search within comments and descriptions

---

### 5.6 Milestones & Releases

**FR-6.1:** Milestone Management

- Create milestones with target dates
- Associate tasks with milestones
- Milestone progress tracking
- Visual timeline of milestones
- Milestone status (Upcoming, Active, Completed, Missed)

**FR-6.2:** Release Planning (for software teams)

- Define releases/sprints
- Sprint duration and dates
- Add tasks to sprint backlog
- Sprint velocity tracking
- Burndown charts
- Sprint retrospectives

---

### 5.7 Collaboration & Communication

**FR-7.1:** Task Comments & Discussions

- Threaded comments on tasks
- Rich text formatting
- @mention users (triggers notification)
- Attach files to comments
- React to comments (emoji reactions)
- Edit/delete own comments
- Pin important comments

**FR-7.2:** Activity Feed

- Real-time activity stream per project
- Filter by activity type (comments, status changes, new tasks)
- User-specific activity feed ("My Activity")
- Subscribe to project activity
- Export activity log

**FR-7.3:** Notifications

| Channel | Description |
|---------|-------------|
| In-app | Real-time notification center |
| Email | Configurable per user |
| Desktop push | Browser permission required |
| Mobile push | Phase 3 |

Notification Triggers:

| Event | Default |
|-------|---------|
| Task assigned to you | On |
| Task status changed | On |
| Due date approaching (1 day, 3 days) | On |
| Someone @mentioned you | On |
| Comment on your task | On |
| Dependency unblocked | On |
| Milestone approaching | On |

**FR-7.4:** Real-time Updates

- Live updates without page refresh
- Show who else is viewing a task
- Collaborative editing indicators
- Conflict resolution for simultaneous edits (see Section 6.5)

---

### 5.8 File & Document Management

**FR-8.1:** File Uploads

| Setting | Value |
|---------|-------|
| Attach files to | Projects, Tasks, Comments |
| Upload method | Drag-and-drop, Browse |
| Supported types | All common formats (PDF, DOC, XLS, IMG, ZIP, etc.) |
| Max file size | 50MB per file (configurable) |
| Workspace storage | 50GB default (expandable) |

**FR-8.2:** File Organization

- Project-level file library
- Folder structure within projects
- File versioning (track changes)
- File preview (images, PDFs)
- Download individual or bulk files
- Search within files (Phase 2)

**FR-8.3:** File Permissions

- Inherit project permissions
- Restrict file access to specific users
- View-only vs download permissions

---

### 5.9 Time Tracking Integration

**FR-9.1:** Task Time Estimation

- Estimated time per task (hours or story points)
- Time tracking per task (via TimeTrack Pro integration)
- Compare estimated vs actual
- Rollup time to project level

**FR-9.2:** TimeTrack Pro Integration

- Bi-directional sync of projects and tasks
- Display time logged per task from TimeTrack Pro
- Time tracking widget in task detail view
- Link to TimeTrack Pro for detailed time entry
- Budget utilization from TimeTrack Pro billing data

---

### 5.10 Reporting & Analytics

**FR-10.1:** Project Manager Dashboards

- My Projects overview
- Tasks by status across all projects
- Overdue tasks
- Upcoming deadlines
- Team workload distribution
- Recent activity

**FR-10.2:** Portfolio Dashboard (Executive View)

- All projects status summary
- Health indicators (On Track, At Risk, Behind)
- Budget utilization
- Resource allocation across projects
- Project timeline visualization
- Key metrics: On-time delivery %, average completion time

**FR-10.3:** Standard Reports

| Report | Description |
|--------|-------------|
| Project Status Report | Progress, milestones, blockers |
| Task Completion Report | Completed tasks by time period |
| Team Performance Report | Tasks completed per user |
| Overdue Tasks Report | All overdue tasks with assignees |
| Velocity Report | Task completion rate over time |
| Budget Report | Hours/cost spent vs planned |
| Time to Completion Report | Average time to complete tasks |
| Dependency Report | Blocked tasks and blockers |

Export Options: PDF, Excel, CSV

**FR-10.4:** Custom Reports & Analytics

- Report builder with drag-and-drop
- Select metrics and dimensions
- Date range filters
- Schedule automated reports via email
- Share reports via link

**FR-10.5:** Project Health Indicators

Automated health score based on:

| Factor | Weight |
|--------|--------|
| % on-time completion | 30% |
| % overdue tasks | 25% |
| Budget utilization | 20% |
| Activity level | 15% |
| Blocker count | 10% |

Display:

- Traffic light system (Green/Yellow/Red)
- Trend arrows (improving/declining)

---

### 5.11 Notifications & Reminders

**FR-11.1:** Notification Center

- Unread notification badge
- Mark as read/unread
- Mark all as read
- Notification grouping
- Notification history (30 days)

**FR-11.2:** Email Digest Options

| Option | Description |
|--------|-------------|
| Daily digest | All activity summary |
| Weekly summary | Weekly activity summary |
| Real-time | Immediate emails |
| Custom schedule | Per user configuration |
| Per-project | Unsubscribe options |

**FR-11.3:** Reminder System

| Reminder Type | Default Timing |
|---------------|----------------|
| Due date approaching | 1 day, 3 days, 1 week before |
| Overdue task | Daily |
| Idle task | No activity in 7 days |
| Milestone approaching | 1 week before |
| Custom reminder | User-defined |

---

### 5.12 Administration & Settings

**FR-12.1:** User Administration

- Add/remove users
- Assign roles and permissions
- Deactivate users (retain data)
- Bulk user import (CSV)
- User activity monitoring
- License/seat management

**FR-12.2:** Workspace Configuration

- Company branding (logo, colors)
- Custom domains (Phase 2)
- Notification defaults
- Time zone and localization
- Fiscal year settings
- Default project settings

**FR-12.3:** Custom Fields

| Field Type | Description |
|------------|-------------|
| Text | Single or multi-line |
| Number | Integer or decimal |
| Date | Date picker |
| Dropdown | Single select |
| Multi-select | Multiple options |
| Checkbox | Boolean |
| URL | Link field |
| User | User reference |

Constraints:

- Maximum 50 custom fields per workspace
- Field name: 1-100 characters
- Dropdown options: max 100 per field
- Apply to tasks, projects, or both
- Required vs optional setting
- Default value configuration

**FR-12.4:** Workflow Customization

- Create custom status workflows
- Define status transitions
- Set required fields per status
- Automated actions on status change

**FR-12.5:** Security & Audit

- Audit log of all system changes
- Export audit logs (CSV)
- Two-factor authentication settings
- Session management
- IP allowlisting (Phase 2)
- Retention period: 3 years

**FR-12.6:** Integrations (Phase 2)

- Webhook configuration
- API key management
- Third-party app connections
- Integration marketplace

---

## 6. Business Rules & Edge Cases

### 6.1 Task State Transitions

**Valid Transitions:**

```
To Do → In Progress → Review → Done
         ↓            ↓
         └→ Blocked ←─┘
              ↓
         (any status when unblocked)
```

| Rule | Behavior |
|------|----------|
| Reopen completed task | Status changes to "To Do", completion date cleared |
| Move to "Done" with incomplete subtasks | Warning displayed, user confirms or cancels |
| Move to "Done" with open blockers | Blocked - must resolve dependencies first |
| Task with missed due date | Auto-tagged as "Overdue", appears in overdue reports |

### 6.2 Project Lifecycle Rules

| Rule | Behavior |
|------|----------|
| Archive project | All tasks become read-only, no new tasks allowed |
| Delete project | Soft delete, recoverable for 30 days, then permanent |
| Complete project | Status changes, tasks remain editable for 7 days |
| Reopen archived project | Admin only, restores full editability |

### 6.3 Dependency Constraints

| Rule | Behavior |
|------|----------|
| Circular dependency | Blocked - system prevents creation |
| Delete task with dependents | Warning shown, user must reassign or remove dependencies |
| Complete task with incomplete dependencies | Blocked unless override by PM |
| Dependency on archived project | Read-only reference maintained |

### 6.4 WIP Limit Enforcement

| Setting | Behavior |
|---------|----------|
| Soft limit | Warning displayed, move allowed |
| Hard limit | Move blocked until column has capacity |
| Override | PM and Admin can override with reason logged |

### 6.5 Real-time Conflict Resolution

**Simultaneous Edit Strategy: Last-Write-Wins with Notification**

| Scenario | Behavior |
|----------|----------|
| Two users editing same field | Last save wins, first user notified of conflict |
| Two users editing different fields | Both changes saved independently |
| User editing while another saves | Merge attempted, conflict shown if same field |

**Conflict Notification:**

```json
{
  "type": "conflict_detected",
  "task_id": "PROJ-123",
  "field": "description",
  "your_value": "...",
  "saved_value": "...",
  "saved_by": "user@example.com",
  "saved_at": "2026-01-13T10:30:00Z",
  "options": ["keep_yours", "accept_theirs", "view_diff"]
}
```

### 6.6 User Deactivation Rules

| Rule | Behavior |
|------|----------|
| Deactivate user | Login blocked, data retained |
| Assigned tasks | Remain assigned, flagged for reassignment |
| Owned projects | Ownership transfer required before deactivation |
| Historical data | Preserved indefinitely |
| Reactivation | Admin can restore full access |

### 6.7 File Management Rules

| Rule | Behavior |
|------|----------|
| Delete file | Soft delete, recoverable for 30 days |
| Storage limit reached | Warning at 80%, block uploads at 100% |
| File version limit | Keep last 10 versions per file |
| Malware detected | File quarantined, uploader notified, admin alerted |

---

## 7. TimeTrack Pro Integration Specification

### 7.1 Integration Overview

ProjectHub integrates with TimeTrack Pro to provide comprehensive time tracking and billing capabilities without duplicating functionality.

| System | Responsibility |
|--------|----------------|
| ProjectHub | Projects, tasks, workflows, collaboration |
| TimeTrack Pro | Time entries, billing rates, timesheets, invoicing |

### 7.2 Data Synchronization

**Projects Sync (ProjectHub → TimeTrack Pro):**

| ProjectHub Field | TimeTrack Pro Field |
|------------------|---------------------|
| project.id | external_project_id |
| project.name | name |
| project.key | project_code |
| project.client_name | client_name |
| project.budget_hours | budget_hours |
| project.status | status |

**Tasks Sync (ProjectHub → TimeTrack Pro):**

| ProjectHub Field | TimeTrack Pro Field |
|------------------|---------------------|
| task.id | external_task_id |
| task.title | name |
| task.project_id | project_id (via mapping) |
| task.estimated_hours | estimated_hours |

**Time Data Sync (TimeTrack Pro → ProjectHub):**

| TimeTrack Pro Field | ProjectHub Display |
|---------------------|-------------------|
| time_entry.hours | task.actual_hours (aggregated) |
| time_entry.billing_rate | task.cost (calculated) |
| project.total_hours | project.hours_logged |

### 7.3 Integration API Endpoints

```
# ProjectHub provides:
POST   /api/integrations/timetrack/sync-projects
POST   /api/integrations/timetrack/sync-tasks
GET    /api/integrations/timetrack/time-summary/:taskId
GET    /api/integrations/timetrack/project-budget/:projectId

# Webhook events ProjectHub sends:
project.created
project.updated
project.archived
task.created
task.updated
task.deleted
task.status_changed
```

### 7.4 Integration Configuration

| Setting | Description |
|---------|-------------|
| TimeTrack Pro API URL | Base URL for TimeTrack Pro API |
| API Key | Service account API key |
| Sync frequency | Real-time (webhook) or scheduled (hourly) |
| Auto-create projects | Create TimeTrack Pro project when ProjectHub project created |
| Billable default | Default billable status for synced tasks |

---

## 8. Non-Functional Requirements

### 8.1 Performance

| Metric | Target |
|--------|--------|
| Page load time | <2 seconds |
| Task creation/update | <1 second |
| Concurrent users | 50+ |
| Kanban board (200+ tasks) | <3 seconds |
| Search results | <2 seconds |
| Real-time update latency | <500ms |

### 8.2 Scalability

- Support 200+ users per workspace
- Handle 100,000+ tasks per workspace
- 50+ active projects simultaneously
- Horizontal scaling capability
- Database query optimization
- Caching layer for frequent queries

### 8.3 Availability

| Metric | Target |
|--------|--------|
| Uptime (business hours) | 99.9% |
| Scheduled maintenance | Sundays 2am-4am |
| Database backups | Every 6 hours |
| Backup retention | 30 days |
| Disaster recovery RPO | 4 hours |

### 8.4 Browser & Device Support

**Desktop Browsers:**

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

**Mobile Browsers:**

- iOS Safari (last 2 versions)
- Chrome Mobile (last 2 versions)

**Minimum Screen Resolutions:**

| Device | Resolution |
|--------|------------|
| Desktop | 1280x800 |
| Tablet | 768x1024 |
| Mobile | 375x667 |

### 8.5 Accessibility

- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatible
- Color contrast requirements met
- Focus indicators visible

---

## 9. Technical Requirements

### 9.1 Recommended Tech Stack

**Frontend:**

- React 18+ with TypeScript
- State management: Redux Toolkit or Zustand
- UI Framework: Material-UI, Ant Design, or Tailwind CSS
- Drag-and-drop: react-beautiful-dnd or dnd-kit
- Rich text editor: Slate.js or TipTap
- Charts: Recharts or Chart.js
- Calendar: FullCalendar or react-big-calendar
- Gantt: react-gantt-chart or custom D3.js

**Backend:**

- Django 5.x with Django REST Framework
- django-rest-framework-simplejwt for JWT authentication
- django-filter for query filtering
- Django Channels for WebSocket/real-time updates
- Celery + Redis for background tasks (notifications, report generation)
- drf-spectacular for OpenAPI documentation
- django-cors-headers for CORS handling

**Database:**

- PostgreSQL (primary database)
- Redis (caching, session storage, real-time features)
- Full-text search: PostgreSQL FTS or Elasticsearch (Phase 2)

**File Storage:**

- AWS S3 or Google Cloud Storage
- CloudFront/CDN for file delivery

**Real-time:**

- Django Channels with WebSocket consumers
- Redis channel layer for distributed pub/sub

**Background Jobs:**

- Celery with Redis broker
- django-celery-beat for scheduled/periodic tasks

**Hosting & Infrastructure:**

- AWS, Google Cloud, or Azure
- Docker containerization
- Kubernetes for orchestration (Phase 2)
- CI/CD: GitHub Actions, GitLab CI, or CircleCI
- Monitoring: DataDog, New Relic, or Sentry
- Logging: ELK stack or CloudWatch

**Email:**

- SendGrid or AWS SES
- Email templates with handlebars

---

### 9.2 API Specification

#### Authentication

```
POST   /api/auth/login              # User login
POST   /api/auth/logout             # User logout
POST   /api/auth/register           # User registration
POST   /api/auth/refresh-token      # Refresh JWT token
POST   /api/auth/forgot-password    # Request password reset
POST   /api/auth/reset-password     # Complete password reset
DELETE /api/auth/sessions           # Revoke all sessions
```

#### Users

```
GET    /api/users                   # List users
GET    /api/users/:id               # Get user details
POST   /api/users                   # Create user (admin)
PUT    /api/users/:id               # Update user
DELETE /api/users/:id               # Deactivate user
GET    /api/users/:id/tasks         # Get user's assigned tasks
GET    /api/users/me                # Current user profile
PUT    /api/users/me                # Update current user
GET    /api/users/me/notifications  # User notification preferences
PUT    /api/users/me/notifications  # Update notification preferences
```

#### Projects

```
GET    /api/projects                # List projects (with filters)
GET    /api/projects/:id            # Get project details
POST   /api/projects                # Create project
PUT    /api/projects/:id            # Update project
DELETE /api/projects/:id            # Archive/delete project
POST   /api/projects/:id/restore    # Restore archived project
GET    /api/projects/:id/tasks      # Get project tasks
GET    /api/projects/:id/members    # Get project members
POST   /api/projects/:id/members    # Add member to project
DELETE /api/projects/:id/members/:userId  # Remove member
GET    /api/projects/:id/files      # Get project files
GET    /api/projects/:id/activity   # Get project activity feed
GET    /api/projects/:id/milestones # Get project milestones
GET    /api/projects/:id/health     # Get project health score
GET    /api/projects/:id/stats      # Get project statistics
```

#### Tasks

```
GET    /api/tasks                   # List tasks (with filters)
GET    /api/tasks/:id               # Get task details
POST   /api/tasks                   # Create task
PUT    /api/tasks/:id               # Update task
DELETE /api/tasks/:id               # Delete task
POST   /api/tasks/:id/restore       # Restore deleted task
PUT    /api/tasks/:id/status        # Update task status
PUT    /api/tasks/:id/assign        # Assign task
PUT    /api/tasks/:id/unassign      # Unassign task
GET    /api/tasks/:id/subtasks      # Get subtasks
POST   /api/tasks/:id/subtasks      # Create subtask
GET    /api/tasks/:id/dependencies  # Get task dependencies
POST   /api/tasks/:id/dependencies  # Add dependency
DELETE /api/tasks/:id/dependencies/:depId  # Remove dependency
GET    /api/tasks/:id/comments      # Get task comments
POST   /api/tasks/:id/comments      # Add comment
GET    /api/tasks/:id/attachments   # Get task attachments
POST   /api/tasks/:id/attachments   # Add attachment
GET    /api/tasks/:id/activity      # Get task activity
POST   /api/tasks/:id/watch         # Watch task
DELETE /api/tasks/:id/watch         # Unwatch task
POST   /api/tasks/bulk              # Bulk create tasks
PUT    /api/tasks/bulk              # Bulk update tasks
DELETE /api/tasks/bulk              # Bulk delete tasks
```

#### Comments

```
GET    /api/comments/:id            # Get comment
PUT    /api/comments/:id            # Update comment
DELETE /api/comments/:id            # Delete comment
POST   /api/comments/:id/reactions  # Add reaction
DELETE /api/comments/:id/reactions/:type  # Remove reaction
```

#### Files

```
POST   /api/files/upload            # Upload file(s)
GET    /api/files/:id               # Get file metadata
GET    /api/files/:id/download      # Download file
GET    /api/files/:id/preview       # Get file preview URL
DELETE /api/files/:id               # Delete file
GET    /api/files/:id/versions      # Get file versions
POST   /api/files/:id/versions      # Upload new version
```

#### Milestones

```
GET    /api/milestones              # List milestones
GET    /api/milestones/:id          # Get milestone details
POST   /api/milestones              # Create milestone
PUT    /api/milestones/:id          # Update milestone
DELETE /api/milestones/:id          # Delete milestone
GET    /api/milestones/:id/tasks    # Get milestone tasks
```

#### Notifications

```
GET    /api/notifications           # List notifications
GET    /api/notifications/unread-count  # Get unread count
PUT    /api/notifications/:id/read  # Mark as read
PUT    /api/notifications/read-all  # Mark all as read
DELETE /api/notifications/:id       # Delete notification
```

#### Reports

```
GET    /api/reports/project-status  # Project status report
GET    /api/reports/task-completion # Task completion report
GET    /api/reports/team-performance # Team performance report
GET    /api/reports/overdue-tasks   # Overdue tasks report
GET    /api/reports/velocity        # Velocity report
GET    /api/reports/portfolio       # Portfolio overview
POST   /api/reports/custom          # Generate custom report
GET    /api/reports/:id/export      # Export report
```

#### Search

```
GET    /api/search                  # Global search
GET    /api/search/tasks            # Search tasks
GET    /api/search/projects         # Search projects
GET    /api/search/files            # Search files
GET    /api/search/suggestions      # Search suggestions
```

#### Workspace & Admin

```
GET    /api/workspace               # Get workspace details
PUT    /api/workspace               # Update workspace
GET    /api/workspace/settings      # Get workspace settings
PUT    /api/workspace/settings      # Update workspace settings
GET    /api/workspace/teams         # List teams
POST   /api/workspace/teams         # Create team
PUT    /api/workspace/teams/:id     # Update team
DELETE /api/workspace/teams/:id     # Delete team
GET    /api/workspace/custom-fields # List custom fields
POST   /api/workspace/custom-fields # Create custom field
PUT    /api/workspace/custom-fields/:id  # Update custom field
DELETE /api/workspace/custom-fields/:id  # Delete custom field
GET    /api/workspace/workflows     # List workflows
POST   /api/workspace/workflows     # Create workflow
PUT    /api/workspace/workflows/:id # Update workflow
DELETE /api/workspace/workflows/:id # Delete workflow
GET    /api/workspace/templates     # List templates
POST   /api/workspace/templates     # Create template
GET    /api/audit/logs              # Get audit logs
POST   /api/audit/export            # Export audit logs
```

#### Integration

```
GET    /api/integrations            # List integrations
POST   /api/integrations/:type/connect    # Connect integration
DELETE /api/integrations/:type/disconnect # Disconnect integration
GET    /api/integrations/webhooks   # List webhooks
POST   /api/integrations/webhooks   # Create webhook
DELETE /api/integrations/webhooks/:id     # Delete webhook
POST   /api/integrations/timetrack/sync   # Trigger TimeTrack sync
```

#### Import/Export

```
POST   /api/import/users            # Bulk import users
POST   /api/import/projects         # Bulk import projects
POST   /api/import/tasks            # Bulk import tasks
GET    /api/import/template/:type   # Download import template
POST   /api/import/validate         # Validate import file
POST   /api/export/projects         # Export projects
POST   /api/export/tasks            # Export tasks
```

---

### 9.3 WebSocket Events

**Client → Server:**

```
join_project          # Subscribe to project updates
leave_project         # Unsubscribe from project
task_editing_start    # Signal task edit in progress
task_editing_stop     # Signal task edit complete
typing_start          # User typing indicator
typing_stop           # User stopped typing
presence_update       # Update user presence status
```

**Server → Client:**

```
task_created          # New task created
task_updated          # Task updated
task_deleted          # Task deleted
task_moved            # Task moved between columns
comment_added         # New comment added
comment_updated       # Comment updated
user_assigned         # User assigned to task
user_unassigned       # User unassigned from task
status_changed        # Task status changed
file_uploaded         # File uploaded
notification_received # New notification
user_presence         # User online/offline status
editing_conflict      # Edit conflict detected
project_updated       # Project settings changed
```

---

### 9.4 Database Schema

#### users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('viewer', 'member', 'project_manager', 'admin')),
    avatar_url VARCHAR(500),
    job_title VARCHAR(100),
    phone VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'busy', 'away', 'off')),
    notification_preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### projects

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    key VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'planning' CHECK (status IN ('planning', 'active', 'on_hold', 'completed', 'archived')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    visibility VARCHAR(20) DEFAULT 'team' CHECK (visibility IN ('private', 'team', 'company')),
    start_date DATE,
    end_date DATE,
    budget_hours DECIMAL(10,2),
    budget_amount DECIMAL(12,2),
    client_name VARCHAR(255),
    team_id INTEGER REFERENCES teams(id),
    workflow_id INTEGER REFERENCES workflows(id),
    settings JSONB DEFAULT '{}',
    health_score INTEGER,
    is_archived BOOLEAN DEFAULT false,
    archived_at TIMESTAMP,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_team ON projects(team_id);
```

#### tasks

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(20) DEFAULT 'task' CHECK (task_type IN ('task', 'bug', 'feature', 'epic', 'story')),
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    assignee_id INTEGER REFERENCES users(id),
    reporter_id INTEGER REFERENCES users(id),
    parent_task_id INTEGER REFERENCES tasks(id),
    milestone_id INTEGER REFERENCES milestones(id),
    due_date DATE,
    estimated_hours DECIMAL(8,2),
    actual_hours DECIMAL(8,2) DEFAULT 0,
    story_points INTEGER,
    position INTEGER DEFAULT 0,
    is_blocked BOOLEAN DEFAULT false,
    blocked_reason TEXT,
    completed_at TIMESTAMP,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
```

#### task_assignments

```sql
CREATE TABLE task_assignments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, user_id)
);
```

#### task_dependencies

```sql
CREATE TABLE task_dependencies (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    depends_on_task_id INTEGER REFERENCES tasks(id) NOT NULL,
    dependency_type VARCHAR(20) DEFAULT 'finish_to_start' CHECK (dependency_type IN ('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id),
    CHECK (task_id != depends_on_task_id)
);
```

#### comments

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    content TEXT NOT NULL,
    parent_comment_id INTEGER REFERENCES comments(id),
    is_pinned BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_task ON comments(task_id);
```

#### comment_reactions

```sql
CREATE TABLE comment_reactions (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER REFERENCES comments(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    reaction_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(comment_id, user_id, reaction_type)
);
```

#### attachments

```sql
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(100),
    file_url VARCHAR(500) NOT NULL,
    storage_key VARCHAR(255) NOT NULL,
    uploaded_by INTEGER REFERENCES users(id) NOT NULL,
    task_id INTEGER REFERENCES tasks(id),
    project_id INTEGER REFERENCES projects(id),
    comment_id INTEGER REFERENCES comments(id),
    folder_path VARCHAR(500),
    version INTEGER DEFAULT 1,
    previous_version_id INTEGER REFERENCES attachments(id),
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attachments_task ON attachments(task_id);
CREATE INDEX idx_attachments_project ON attachments(project_id);
```

#### project_members

```sql
CREATE TABLE project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);
```

#### teams

```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### team_members

```sql
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id)
);
```

#### milestones

```sql
CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'completed', 'missed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### workflows

```sql
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    statuses JSONB NOT NULL,
    transitions JSONB,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### custom_fields

```sql
CREATE TABLE custom_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) NOT NULL CHECK (field_type IN ('text', 'number', 'date', 'dropdown', 'multi_select', 'checkbox', 'url', 'user')),
    options JSONB,
    is_required BOOLEAN DEFAULT false,
    applies_to VARCHAR(20) NOT NULL CHECK (applies_to IN ('task', 'project', 'both')),
    default_value TEXT,
    validation_rules JSONB,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### custom_field_values

```sql
CREATE TABLE custom_field_values (
    id SERIAL PRIMARY KEY,
    custom_field_id INTEGER REFERENCES custom_fields(id) NOT NULL,
    entity_id INTEGER NOT NULL,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('task', 'project')),
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(custom_field_id, entity_id, entity_type)
);
```

#### tags

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);
```

#### task_tags

```sql
CREATE TABLE task_tags (
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    tag_id INTEGER REFERENCES tags(id) NOT NULL,
    PRIMARY KEY (task_id, tag_id)
);
```

#### notifications

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link VARCHAR(500),
    metadata JSONB,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
```

#### activity_log

```sql
CREATE TABLE activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    project_id INTEGER REFERENCES projects(id),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_log_project ON activity_log(project_id);
CREATE INDEX idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_log_date ON activity_log(created_at);
```

#### workspace_settings

```sql
CREATE TABLE workspace_settings (
    id SERIAL PRIMARY KEY,
    workspace_name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    settings JSONB DEFAULT '{}',
    storage_used BIGINT DEFAULT 0,
    storage_limit BIGINT DEFAULT 53687091200, -- 50GB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### task_watchers

```sql
CREATE TABLE task_watchers (
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, user_id)
);
```

#### task_checklists

```sql
CREATE TABLE task_checklists (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    position INTEGER DEFAULT 0,
    completed_by INTEGER REFERENCES users(id),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 9.5 API Response Standards

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
                "field": "title",
                "message": "Task title is required"
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
| sort | created_at | - | Sort field |
| order | desc | - | Sort order (asc/desc) |

---

### 9.6 Error Handling Standards

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
| AUTH_006 | Invalid token | Malformed or invalid JWT |

**Validation Errors (VAL)**

| Code | Message | Description |
|------|---------|-------------|
| VAL_001 | Required field missing | Mandatory field not provided |
| VAL_002 | Invalid format | Field format incorrect |
| VAL_003 | Value out of range | Value exceeds allowed limits |
| VAL_004 | Duplicate entry | Unique constraint violated |
| VAL_005 | Invalid reference | Foreign key doesn't exist |
| VAL_006 | Invalid file type | File type not allowed |
| VAL_007 | File too large | Exceeds size limit |

**Business Logic Errors (BIZ)**

| Code | Message | Description |
|------|---------|-------------|
| BIZ_001 | Project archived | Cannot modify archived project |
| BIZ_002 | Circular dependency | Would create circular reference |
| BIZ_003 | WIP limit exceeded | Column at capacity |
| BIZ_004 | Cannot delete with dependents | Task has dependencies |
| BIZ_005 | Cannot complete blocked task | Dependencies not resolved |
| BIZ_006 | Ownership transfer required | Must transfer before action |
| BIZ_007 | Storage limit reached | Workspace at storage capacity |
| BIZ_008 | Edit conflict | Another user modified resource |

**Not Found Errors (NOT)**

| Code | Message | Description |
|------|---------|-------------|
| NOT_001 | Resource not found | Requested entity doesn't exist |
| NOT_002 | Project not found | Project ID invalid |
| NOT_003 | Task not found | Task ID invalid |
| NOT_004 | User not found | User ID invalid |
| NOT_005 | File not found | File ID invalid |

**System Errors (SYS)**

| Code | Message | Description |
|------|---------|-------------|
| SYS_001 | Database error | Database operation failed |
| SYS_002 | External service unavailable | Third-party API down |
| SYS_003 | Rate limit exceeded | Too many requests |
| SYS_004 | File storage error | S3/storage operation failed |
| SYS_005 | Real-time connection error | WebSocket failure |

---

## 10. UI/UX Requirements

### 10.1 Navigation Structure

**Top Navigation Bar:**

```
[Logo] [Workspace Name ▼] | Dashboard | Projects | My Tasks | Reports | [Search 🔍] | [+ New] | [Notifications 🔔] | [Profile 👤]
```

**Left Sidebar (Collapsible):**

```
Home
├─ Dashboard
├─ My Tasks
├─ My Projects
├─ Calendar

Projects
├─ All Projects
├─ Starred
├─ Recently Viewed
└─ [+ New Project]

Teams
├─ Engineering
├─ Marketing
└─ Design

Reports (Manager/Admin)
├─ Portfolio Dashboard
├─ Project Reports
└─ Team Performance

Settings (Admin)
├─ Users
├─ Teams
├─ Workspace Settings
└─ Integrations
```

### 10.2 Key Screen Wireframes

**Dashboard (Home Page):**

```
┌────────────────────────────────────────────────────────────┐
│ Welcome back, Alex!                                         │
│                                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│ │My Tasks  │ │Overdue   │ │Due This  │ │Completed │      │
│ │    24    │ │    3     │ │Week  7   │ │This Wk 12│      │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                             │
│ My Tasks Due Today (3)                   [View All →]      │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ ☐ Design homepage mockup        [Website Redesign] │   │
│ │ ☐ Review pull request #234      [Mobile App]       │   │
│ │ ☐ Update documentation          [API v2]           │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ My Projects (5)                          [View All →]      │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐              │
│ │Website │ │Mobile  │ │Q1      │ │Product │              │
│ │Redesign│ │App     │ │Campaign│ │Launch  │              │
│ │● 67%   │ │● 45%   │ │● 89%   │ │● 23%   │              │
│ └────────┘ └────────┘ └────────┘ └────────┘              │
│                                                             │
│ Recent Activity                                             │
│ • Sarah updated task "Homepage Design" 5 mins ago          │
│ • Mike commented on "API Integration" 1 hour ago           │
│ • You completed "Database Schema" 2 hours ago              │
└────────────────────────────────────────────────────────────┘
```

**Project Board (Kanban View):**

```
┌──────────────────────────────────────────────────────────────┐
│ Website Redesign                    [List][Kanban][Timeline] │
│ 42 tasks • 23 completed • 5 team members                     │
│                                                               │
│ To Do (8)  │ In Progress (5) │ Review (3)   │ Done (12)     │
│ ───────────┼─────────────────┼──────────────┼───────────    │
│ ┌────────┐│ ┌────────┐      │ ┌────────┐   │ ┌────────┐   │
│ │WEB-234 ││ │WEB-231 │      │ │WEB-228 │   │ │WEB-201 │   │
│ │Homepage││ │Mobile  │      │ │Footer  │   │ │Research│   │
│ │Design  ││ │Menu    │      │ │Design  │   │ │Phase   │   │
│ │👤 Sarah││ │👤 Mike │      │ │👤 Alex │   │ │✓       │   │
│ │📅 Jan15││ │📅 Jan14│      │ │📅 Jan13│   │ │        │   │
│ └────────┘│ └────────┘      │ └────────┘   │ └────────┘   │
│           │                 │              │              │
│ ┌────────┐│ ┌────────┐      │ ┌────────┐   │ ┌────────┐   │
│ │WEB-235 ││ │WEB-232 │      │ │WEB-229 │   │ │WEB-202 │   │
│ │Contact ││ │Payment │      │ │Header  │   │ │Wireframe   │
│ │Form    ││ │Gateway │      │ │Nav     │   │ │✓       │   │
│ │👤 Alex ││ │👤 Sarah│      │ │👤 Mike │   │ │        │   │
│ │📅 Jan16││ │⚠️ Overdue      │ │📅 Jan14│   │ └────────┘   │
│ └────────┘│ └────────┘      │ └────────┘   │              │
│           │                 │              │              │
│ [+ Add]   │ [+ Add]         │ [+ Add]      │              │
└───────────┴─────────────────┴──────────────┴──────────────┘
```

**Task Detail Modal:**

```
┌──────────────────────────────────────────────────────────┐
│ WEB-234: Design Homepage Layout                    [X]    │
├──────────────────────────────────────────────────────────┤
│ Project: Website Redesign    Type: Task    Priority: High│
│                                                            │
│ ┌─ Description ──────────────────────────────────────┐   │
│ │ Create a modern, responsive homepage design that    │   │
│ │ aligns with our new brand guidelines.               │   │
│ │                                                      │   │
│ │ Requirements:                                        │   │
│ │ • Hero section with CTA                             │   │
│ │ • Feature highlights                                │   │
│ │ • Testimonials section                              │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                            │
│ Assignee: 👤 Sarah Johnson   Due: 📅 Jan 15, 2026        │
│ Status: [In Progress ▼]     Priority: [High ▼]           │
│ Estimated: 8h  Logged: 3.5h                               │
│                                                            │
│ ┌─ Activity (12) ─────────────────────────────────────┐  │
│ │ 💬 Mike Chen: "Looks great! Small note on colors"   │  │
│ │    2 hours ago                          [Reply]      │  │
│ │                                                      │  │
│ │ ✏️ Sarah updated status: To Do → In Progress        │  │
│ │    3 hours ago                                       │  │
│ │                                                      │  │
│ │ 📎 Sarah added attachment: homepage_v1.fig          │  │
│ │    Yesterday at 4:23pm                               │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ 📎 Attachments (2)    ✓ Checklist (3/5)    🔗 Links (1)  │
│                                                            │
│ [Add Comment...]                              [Update]    │
└──────────────────────────────────────────────────────────┘
```

**Timeline/Gantt View:**

```
┌────────────────────────────────────────────────────────────┐
│ Website Redesign - Timeline View        [Week|Month|Quarter]│
│                                                             │
│              Week 1    Week 2    Week 3    Week 4          │
│              |---------|---------|---------|---------|      │
│                                                             │
│ Research     ████████                                       │
│ Design       ░░░░░░░░░░████████████                        │
│ Development           ░░░░░░░░░░████████████████           │
│ Testing                              ░░░░░░████████        │
│ Launch                                      ░░░░░░░░◆      │
│                                                     ↑       │
│                                                  Today      │
│                                                             │
│ Legend: ████ Completed  ░░░░ Planned  ◆ Milestone          │
└────────────────────────────────────────────────────────────┘
```

### 10.3 Design System

**Color Palette:**

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #2563EB | Buttons, links, active states |
| Secondary | #7C3AED | Accents, badges |
| Success | #10B981 | Completed, positive |
| Warning | #F59E0B | Warnings, attention |
| Danger | #EF4444 | Errors, critical |
| Neutral | #6B7280 | Text, borders |

**Priority Colors:**

| Priority | Color |
|----------|-------|
| Critical | Red (#EF4444) |
| High | Orange (#F59E0B) |
| Medium | Yellow (#EAB308) |
| Low | Blue (#3B82F6) |

**Status Colors:**

| Status | Color |
|--------|-------|
| To Do | Gray (#6B7280) |
| In Progress | Blue (#2563EB) |
| Review | Purple (#7C3AED) |
| Done | Green (#10B981) |
| Blocked | Red (#EF4444) |

**Typography:**

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Headings | Inter/Roboto | 600-700 | 18-32px |
| Body | Inter/Roboto | 400 | 14-16px |
| Code | Fira Code | 400 | 14px |

**Spacing:**

- Base unit: 4px
- Common spacing: 8px, 16px, 24px, 32px, 48px

**Components:**

| Component | Specification |
|-----------|---------------|
| Border radius (cards) | 8px |
| Border radius (buttons) | 4px |
| Shadows | Subtle elevation |
| Loading states | Skeleton screens or spinners |
| Empty states | Illustration + CTA |

**Responsive Breakpoints:**

| Device | Range |
|--------|-------|
| Mobile | 320px - 767px |
| Tablet | 768px - 1023px |
| Desktop | 1024px+ |

---

## 11. Security & Compliance

### 11.1 Authentication Security

| Measure | Implementation |
|---------|----------------|
| Password hashing | bcrypt (cost 12+) |
| Token type | JWT with short expiry (15 min) + refresh tokens |
| Cookies | Secure, httpOnly |
| Password strength | 10+ chars, complexity rules |
| Account lockout | 5 attempts → 30-min lockout |
| Reset token expiry | 1 hour |

### 11.2 Password Requirements

**Minimum Requirements:**

| Requirement | Specification |
|-------------|---------------|
| Length | 10+ characters |
| Uppercase | At least 1 (A-Z) |
| Lowercase | At least 1 (a-z) |
| Numbers | At least 1 (0-9) |
| Special | At least 1 (!@#$%^&*) |
| Blocklist | Not in common password list |
| History | Cannot reuse last 5 passwords |

### 11.3 Session Management

| Setting | Value |
|---------|-------|
| JWT expiry | 15 minutes |
| Refresh token expiry | 7 days |
| Concurrent sessions | Max 5 per user |
| Password change | Invalidates all sessions |
| Session revocation | Admin API available |

**Security Headers:**

| Header | Value |
|--------|-------|
| Secure | true (HTTPS only) |
| HttpOnly | true |
| SameSite | Strict |
| CSRF | Token validation required |

### 11.4 Authorization

- Role-based access control (RBAC)
- Project-level permissions
- Check permissions on every API call
- No client-side only authorization
- Database row-level security

### 11.5 Data Security

| Measure | Implementation |
|---------|----------------|
| Transport | TLS 1.3 encryption |
| At rest | AES-256 encryption (sensitive fields) |
| File upload | Type validation, malware scan |
| Input | Sanitization and validation |
| Output | Encoding (prevent XSS) |
| SQL | Parameterized queries |
| CSRF | Tokens on all forms |
| CSP | Content Security Policy headers |
| Audits | Regular security audits |
| Dependencies | Vulnerability scanning |

### 11.6 File Security

| Measure | Implementation |
|---------|----------------|
| Malware scanning | On upload |
| File types | Allowlist only |
| File names | Randomized (prevent traversal) |
| Storage domain | Separate (prevent XSS) |
| Download URLs | Signed, time-limited |
| Encryption | At rest |

### 11.7 Privacy & Compliance

| Requirement | Implementation |
|-------------|----------------|
| GDPR Article 17 | Right to Erasure |
| GDPR Article 20 | Data Portability |
| DPA | Data Processing Agreement templates |
| Cookies | Consent management |
| Privacy policy | Required acknowledgment |
| Audit logs | Compliance records |
| Data retention | Configurable policies |
| Third-party | Disclosure required |

---

## 12. Success Metrics & KPIs

### 12.1 Adoption Metrics

| Metric | Target |
|--------|--------|
| User activation | 95% within 45 days |
| Daily active users | 85% |
| Projects created per week | 10+ |
| Tasks created per user per week | 15+ |

### 12.2 Engagement Metrics

| Metric | Target |
|--------|--------|
| Average session duration | 25+ minutes |
| Return visits per day | 4+ |
| Comments per task | 2+ |
| File uploads per project | 10+ |

### 12.3 Productivity Metrics

| Metric | Target |
|--------|--------|
| Tasks completed on time | 80% |
| Task completion time decrease | 20% |
| Projects delivered on time | 90% |
| Status meeting reduction | 50% |

### 12.4 Quality Metrics

| Metric | Target |
|--------|--------|
| User satisfaction (NPS) | 40+ |
| Feature adoption rate | 70% |
| Support tickets per week | <2 |
| Bug reports per sprint | <5 |

### 12.5 Business Metrics

| Metric | Target |
|--------|--------|
| Project delivery rate | 90% on time |
| Resource utilization | 75-85% |
| ROI | Positive within 6 months |
| Team productivity increase | 20% |

---

## 13. Development Phases

### Phase 1: Core MVP

**Authentication & Users:**

- User registration/login
- Password reset
- User profiles
- Basic RBAC (Admin, Manager, Member)

**Projects:**

- Create/edit projects
- Project dashboard
- Project members

**Tasks:**

- Create/edit/delete tasks
- Task assignments
- Status workflow (To Do, In Progress, Done)
- Due dates
- Basic task details

**Views:**

- List view with filters
- Basic Kanban board
- Task detail modal

**Notifications:**

- In-app notifications
- Email notifications (task assigned, mentioned)

**Deliverable:** Functional project management tool with task tracking

---

### Phase 2: Enhanced Features

**Advanced Task Features:**

- Subtasks
- Task dependencies
- Task templates
- Bulk operations
- Tags/labels

**Additional Views:**

- Calendar view
- Table view
- Timeline/Gantt chart (basic)

**Collaboration:**

- Comments with @mentions
- File attachments
- Activity feed
- Real-time updates

**Reporting:**

- Project status dashboard
- Task completion reports
- Basic analytics

**Deliverable:** Feature-rich collaboration platform

---

### Phase 3: Advanced & Scale

**Milestones & Planning:**

- Milestone tracking
- Sprint/release planning
- Burndown charts

**Advanced Reporting:**

- Custom report builder
- Portfolio dashboard
- Team performance analytics
- Export capabilities

**Workflow Customization:**

- Custom workflows per project
- Custom fields
- Workflow automation

**Performance:**

- Query optimization
- Caching layer
- Load testing

**Mobile:**

- Mobile-optimized responsive design
- Touch gestures for drag-and-drop

**Deliverable:** Enterprise-ready PM platform

---

### Phase 4: Integrations & Polish

**Integrations:**

- Webhook system
- REST API documentation
- TimeTrack Pro integration
- Slack notifications
- Email integration (create tasks via email)

**Advanced Features:**

- Search across all content
- Saved filters and views
- Recurring tasks
- Task automation rules

**Polish:**

- User onboarding flow
- Help documentation
- Video tutorials
- Performance monitoring
- Beta testing

**Deliverable:** Production-ready with integrations

---

### Phase 5: Post-Launch

- Mobile native apps (iOS/Android)
- SSO (SAML, OAuth)
- Advanced time tracking
- Resource management
- Budget tracking
- Risk management
- Advanced automation
- AI-powered insights
- Third-party app marketplace

---

## 14. Out of Scope (v1.0)

The following are NOT included in v1.0:

| Feature | Status | Future Phase |
|---------|--------|--------------|
| Native mobile apps | Responsive web only | Phase 5 |
| Advanced resource management | Not included | Phase 5 |
| Budget/financial tracking | Basic only | Phase 5 |
| Invoice generation | Not included | - |
| Client portal | Not included | Future |
| Advanced time tracking | Via TimeTrack Pro | - |
| Advanced automation | Not included | Phase 5 |
| AI-powered features | Not included | Phase 5 |
| Video conferencing | Not included | - |
| Built-in chat | Not included | - |
| Advanced portfolio management | Not included | Phase 5 |
| Multi-workspace support | Not included | Future |
| White-labeling | Not included | Future |
| On-premise deployment | Not included | Future |
| Field-level permissions | Not included | Future |
| Custom roles | Predefined only | Future |
| Critical path analysis | Not included | Future |
| Agile metrics (velocity, cumulative flow) | Basic only | Phase 3 |

---

## 15. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| Project | Container for related tasks and work |
| Task | Individual work item with status, assignee, due date |
| Epic | Large body of work containing multiple tasks |
| Sprint | Time-boxed period for completing work (Agile) |
| Milestone | Significant checkpoint or deliverable |
| Backlog | Collection of tasks not yet started |
| WIP Limit | Maximum tasks allowed in a status column |
| Burndown Chart | Visual showing remaining work vs time |
| Story Points | Estimation unit for task complexity |
| Assignee | Person responsible for completing a task |
| Watcher | Person subscribed to task updates |
| Blocker | Issue preventing task completion |
| Dependency | Task that must be completed before another |

### B. Sample User Flows

**Flow 1: Create New Project**

1. User clicks "+ New" → "Project"
2. Modal opens with project creation form
3. User enters: Name, description, dates, assigns manager
4. User selects team members
5. User chooses project template or starts blank
6. Clicks "Create Project"
7. Redirected to project board
8. Team members receive notification

**Flow 2: Create and Assign Task**

1. User on project Kanban board
2. Clicks "+ Add" in "To Do" column
3. Quick create modal appears
4. User enters task title, selects assignee
5. Clicks "Create" (or Enter key)
6. Task appears in column
7. User clicks task to open detail view
8. Adds description, due date, attachments
9. Assignee receives notification

**Flow 3: Complete Task Workflow**

1. Assignee sees task in "My Tasks"
2. Clicks task to open detail
3. Reviews requirements, adds comment with update
4. Drags task to "In Progress" status
5. Works on task, logs time (via TimeTrack Pro)
6. Uploads deliverable file
7. Drags to "Review" status
8. Manager receives notification
9. Manager reviews, adds approval comment
10. Manager moves to "Done"
11. Task marked complete, team notified

**Flow 4: Handle Edit Conflict**

1. User A opens task detail
2. User B opens same task detail
3. User A edits description, saves
4. User B edits same description, saves
5. User B receives conflict notification
6. Options presented: Keep yours, Accept theirs, View diff
7. User B chooses, conflict resolved
8. Activity log records both edits

---

## 16. AI Assistant Development Instructions

When developing this application:

### 1. Start with Phase 1 MVP

Focus on core functionality first:

- Authentication and authorization
- Basic project and task management
- List and Kanban views
- In-app notifications

### 2. Follow Best Practices

**Frontend:**

- Component-based architecture
- Separate presentational and container components
- Global state management for shared data
- Local state for component-specific data
- Memoization for performance
- Lazy loading for routes

**Backend (Django):**

- Use Django REST Framework ViewSets for CRUD operations
- API versioning via URL prefix (/api/v1/)
- Use Django signals sparingly (prefer explicit method calls)
- Leverage django-filter for query parameter filtering
- Use select_related() and prefetch_related() to avoid N+1 queries
- Database transactions with atomic() for data integrity
- Custom permission classes for fine-grained access control
- Use Celery tasks for long-running operations
- Django Channels consumers for WebSocket handling

**Django Project Structure:**

```
projecthub/
├── config/                 # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py             # For Django Channels
│   └── routing.py          # WebSocket routing
├── apps/
│   ├── users/              # User management, auth
│   ├── workspaces/         # Workspace management
│   ├── projects/           # Projects, milestones
│   ├── tasks/              # Tasks, subtasks, dependencies
│   ├── comments/           # Comments, reactions
│   ├── files/              # File attachments
│   ├── notifications/      # In-app notifications
│   ├── activity/           # Activity feeds
│   ├── integrations/       # TimeTrack Pro, third-party
│   └── reports/            # Dashboards, analytics
├── core/                   # Shared utilities, base models
│   ├── models.py           # Abstract base models
│   ├── permissions.py      # Custom DRF permissions
│   ├── pagination.py       # Custom pagination classes
│   └── exceptions.py       # Custom exception handlers
└── manage.py
```

**Security:**

- Never trust client-side data
- Validate and sanitize all inputs
- Use parameterized queries
- Implement proper CORS policies
- Rate limiting on sensitive endpoints

**Testing:**

- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Test coverage goal: 70%+

### 3. Performance Optimization

- Database query optimization (use EXPLAIN)
- Implement caching strategy (Redis)
- Pagination for large lists
- Debounce search inputs
- Optimize images and assets
- Use CDN for static files
- Lazy load components

### 4. Real-time Features (Django Channels)

- Use Django Channels with Redis channel layer
- WebSocket consumers for each real-time feature:
  - TaskConsumer: task updates, status changes
  - ProjectConsumer: project-level events
  - NotificationConsumer: user notifications
  - PresenceConsumer: online status tracking
- Reconnection logic with exponential backoff (frontend)
- Optimistic UI updates with server reconciliation
- Conflict resolution (last-write-wins with notification)
- Group-based broadcasting (project members, task watchers)

### 5. Deliverables

- Django migration files (apps/*/migrations/)
- API documentation via drf-spectacular (Swagger/ReDoc)
- Environment variables template (.env.example)
- README with setup instructions
- Docker Compose configuration (Django + Postgres + Redis + Celery)
- Deployment guide (Gunicorn/Daphne + Nginx)
- User documentation
- Admin guide

### 6. Questions to Clarify

- Hosting environment details
- Integration requirements with existing systems
- Specific business rules or workflows
- Design preferences (provide mockups if available)
- TimeTrack Pro integration priority

### 7. Development Workflow

- Use Git with feature branches
- Meaningful commit messages
- Code reviews before merging
- CI/CD pipeline setup
- Staging environment for testing
- Production deployment checklist

---

**END OF PRD**
