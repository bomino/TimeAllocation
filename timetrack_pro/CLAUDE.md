# TimeTrack Pro - AI Assistant Guidelines

## Project Overview

**Project**: TimeTrack Pro - Employee Time Allocation & Timesheet Management
**Type**: Full-stack web application
**Repository**: https://github.com/bomino/TimeAllocation

## Tech Stack

### Backend
- Python 3.12, Django 5.0+, Django REST Framework 3.14+
- PostgreSQL 15, Redis 7, Celery 5.3+
- JWT Authentication (SimpleJWT)
- drf-spectacular for API documentation

### Frontend
- React 19, TypeScript 5.9, Vite 7
- TanStack Query 5 (server state), Zustand 5 (client state)
- React Hook Form + Zod (forms/validation)
- Tailwind CSS 4, Radix UI (components)
- Recharts (charts), Lucide React (icons)

### Infrastructure
- Docker & Docker Compose
- Nginx (frontend), Gunicorn (backend)

## Project Structure

```
timetrack_pro/
├── apps/                    # Django apps
│   ├── users/              # Auth, user management
│   ├── companies/          # Organization entities
│   ├── projects/           # Project management
│   ├── rates/              # Billing rates
│   ├── timeentries/        # Time entries & timer
│   ├── timesheets/         # Timesheet workflow
│   ├── reports/            # Analytics
│   └── infrastructure/     # Shared utilities
├── config/                  # Django settings
│   ├── settings/
│   │   ├── base.py         # Common settings
│   │   ├── development.py  # Dev config
│   │   ├── production.py   # Prod config
│   │   └── test.py         # Test config
│   └── urls.py             # URL routing
├── core/                    # Shared Django utilities
├── frontend/               # React application
│   └── src/
│       ├── features/       # Feature modules (auth, dashboard, etc.)
│       ├── components/     # UI components
│       ├── hooks/          # Custom hooks
│       ├── lib/            # Utilities
│       ├── routes/         # Route config
│       └── types/          # TypeScript types
├── docker-compose.yml      # Container orchestration
└── Dockerfile              # Backend container
```

## Development Commands

### Docker
```bash
docker-compose up -d                    # Start all services
docker-compose build backend --no-cache # Rebuild backend (code is copied, not mounted)
docker-compose logs -f backend          # View backend logs
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Backend (local)
```bash
python manage.py runserver              # Dev server
pytest                                   # Run tests
pytest --cov=apps --cov=core            # With coverage
ruff check .                             # Lint
ruff check . --fix                       # Auto-fix
mypy apps/ config/ core/                # Type check
```

### Frontend
```bash
cd frontend
npm run dev                              # Dev server (port 5173)
npm run build                            # Production build
npm run lint                             # ESLint
```

## Service Ports

| Service | Port | Notes |
|---------|------|-------|
| Frontend | 3080 | Nginx serving React |
| Backend | 8088 | Django API |
| PostgreSQL | 5440 | Dev database |
| PostgreSQL (test) | 5441 | Test database |
| Redis | 6400 | Cache/broker |

## Key Patterns

### Backend

**API Response Format:**
```python
{
    "success": True,
    "data": [...],  # or single object
    "meta": {"page": 1, "page_size": 20, "total": 100}
}
```

**ViewSet Pattern:**
```python
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return Project.objects.filter(
            company=self.request.user.company,
            status=Project.Status.ACTIVE,
        ).order_by('name')
```

**URL Registration:**
```python
# apps/{app}/urls.py
router = DefaultRouter()
router.register(r'', ViewSet, basename='name')
urlpatterns = [path('', include(router.urls))]

# config/urls.py
path('api/v1/{app}/', include('apps.{app}.urls')),
```

### Frontend

**API Client:**
```typescript
// Uses Axios with JWT interceptor
import apiClient from '@/lib/api-client'

const response = await apiClient.get<{ success: boolean; data: T[] }>('/endpoint/')
return response.data.data ?? []
```

**TanStack Query Pattern:**
```typescript
const { data, isLoading } = useQuery({
    queryKey: ['resource', { filter }],
    queryFn: async () => {
        const response = await apiClient.get<ApiResponse>('/resource/', { params })
        return response.data.data ?? []
    },
})
```

**Form with Zod:**
```typescript
const schema = z.object({
    field: z.string().min(1, 'Required'),
})
type FormData = z.infer<typeof schema>

const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { field: '' },
})
```

**Role-Based Logic:**
```typescript
const { isAdmin, isManager, isEmployee } = useAuth()
```

## Business Rules

### Date Validation for Time Entries
- **Employees**: Current week + 1 week back
- **Admins**: Current week + 1 month back
- Week starts on Monday (`weekStartsOn: 1`)

### User Roles
| Role | Permissions |
|------|-------------|
| EMPLOYEE | Own time entries, submit timesheets |
| MANAGER | + Approve team timesheets, team reports |
| ADMIN | Full system access |

### Billing Rate Hierarchy
1. Employee-Project specific rate
2. Project default rate
3. Employee default rate
4. Company default rate

## Testing

**Pytest Fixtures:**
- `api_client` - Unauthenticated
- `authenticated_client` - As employee
- `authenticated_manager_client` - As manager
- `authenticated_admin_client` - As admin
- `test_clock` - Time travel

## Common Tasks

### Add New API Endpoint
1. Create/update model in `apps/{app}/models.py`
2. Create serializer in `apps/{app}/serializers.py`
3. Create viewset in `apps/{app}/views.py`
4. Register in `apps/{app}/urls.py`
5. Include in `config/urls.py` if new app
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`
7. Rebuild Docker if needed: `docker-compose build backend --no-cache`

### Add New Frontend Feature
1. Create feature folder in `frontend/src/features/{feature}/`
2. Add components, hooks, api files
3. Register routes in `frontend/src/routes/index.tsx`
4. Add navigation in `frontend/src/components/layout/Sidebar.tsx`

### Add shadcn/ui Component
```bash
cd frontend
npx shadcn@latest add {component}
```

## Environment Variables

**Required:**
- `SECRET_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

**Optional:**
- `DJANGO_SETTINGS_MODULE` (default: `config.settings.development`)
- `REDIS_URL` (default: `redis://localhost:6379/0`)
- `FRONTEND_URL` (default: `http://localhost:3000`)

## Code Style

### Backend
- Follow PEP 8 (enforced by Ruff)
- Use type hints
- Docstrings for public APIs only

### Frontend
- ESLint + TypeScript strict mode
- No `any` types
- Prefer function components with hooks
- Use path aliases (`@/components/...`)

## Important Notes

- Backend Docker container copies code (no volume mount) - rebuild after changes
- Frontend uses Vite with hot reload in dev
- API docs available at `/api/docs/` (Swagger UI)
- All API endpoints require authentication except login/register
