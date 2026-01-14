# TimeTrack Pro

Enterprise time tracking and timesheet management application.

## Tech Stack

**Backend:**
- Django 5.2 + Django REST Framework
- PostgreSQL 15
- Redis 7 (Celery broker)
- JWT authentication (SimpleJWT)
- drf-spectacular (OpenAPI docs)

**Frontend:**
- React 18 + TypeScript
- Vite
- TanStack Query (data fetching)
- Tailwind CSS v4
- shadcn/ui + Radix UI
- Recharts (charts)
- React Hook Form + Zod

## Project Structure

```
timetrack_pro/
├── apps/
│   ├── users/          # User model, auth, roles
│   ├── companies/      # Company/tenant model
│   ├── projects/       # Project management
│   ├── rates/          # Billing rate resolution
│   ├── timeentries/    # Time entry CRUD
│   ├── timesheets/     # Weekly timesheet workflow
│   └── reports/        # Analytics endpoints
├── config/
│   ├── settings/       # Django settings (base, dev, prod)
│   └── urls.py         # Root URL config
├── core/               # Shared utilities, pagination, exceptions
├── frontend/           # React SPA
│   └── src/
│       ├── components/ # UI components (layout, ui)
│       ├── features/   # Feature modules (dashboard, time-entries, etc.)
│       ├── lib/        # Utilities, API client
│       └── types/      # TypeScript types
├── docker-compose.yml
└── Dockerfile
```

## Docker Commands

```bash
# Start all services
docker-compose up -d

# Rebuild backend after code changes
docker-compose build backend && docker-compose up -d backend

# View logs
docker-compose logs backend --tail=50
docker-compose logs frontend --tail=50

# Restart specific service
docker-compose restart backend

# Run Django management commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell
```

## Service Ports

| Service  | Port  | URL                           |
|----------|-------|-------------------------------|
| Frontend | 3080  | http://localhost:3080         |
| Backend  | 8088  | http://localhost:8088         |
| API Docs | 8088  | http://localhost:8088/api/docs/ |
| Postgres | 5440  | localhost:5440                |
| Redis    | 6400  | localhost:6400                |

## API Structure

All API endpoints prefixed with `/api/v1/`:

- `/auth/login/`, `/auth/refresh/`, `/auth/logout/`
- `/users/`, `/users/me/`
- `/projects/`
- `/time-entries/`
- `/timesheets/`, `/timesheets/{id}/submit/`, `/timesheets/{id}/approve/`
- `/rates/`
- `/reports/hours/summary/`, `/reports/approval/metrics/`

## User Roles

| Role     | Permissions                                    |
|----------|------------------------------------------------|
| EMPLOYEE | Own time entries, own timesheets               |
| MANAGER  | + View/approve team timesheets, view reports   |
| ADMIN    | + All users, rates, company settings           |

## Frontend Patterns

**API Client:** `frontend/src/lib/api-client.ts`
- Axios with JWT interceptors
- Auto token refresh on 401

**Data Fetching:** TanStack Query
```tsx
const { data, isLoading } = useQuery({
  queryKey: ['time-entries'],
  queryFn: () => apiClient.get('/time-entries/'),
})
```

**Mutations:**
```tsx
const mutation = useMutation({
  mutationFn: (data) => apiClient.post('/time-entries/', data),
  onSuccess: () => queryClient.invalidateQueries(['time-entries']),
})
```

## UI Design System

**Style:** Modern Corporate (Linear/Stripe inspired)
- Dark sidebar (`bg-slate-900`)
- Light content area (`bg-background-subtle`)
- Primary color: Indigo (`hsl(238 73% 60%)`)
- No gradients or glassmorphism

**Fonts:**
- Body: Manrope
- Monospace (numbers): JetBrains Mono

**Component sizing:** Compact (h-9 buttons/inputs)

## Development Notes

- Backend code is baked into Docker image (not volume mounted)
- Must rebuild container after Python code changes
- Frontend hot-reloads automatically in dev
- Tailwind v4 uses `@theme` block for CSS variables
- Custom CSS variable utilities (like `bg-sidebar`) don't auto-generate in Tailwind v4 - use standard color classes instead

## Test Users

Created via seed data or `createsuperuser`:
- Admin: Check Django admin or create with management command
