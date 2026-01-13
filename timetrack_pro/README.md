# TimeTrack Pro

A comprehensive employee time allocation and timesheet management system built with Django REST Framework and React.

## Features

- **Time Tracking**: Log work hours with optional timer functionality
- **Timesheet Management**: Submit, approve, and reject timesheets with approval workflow
- **Role-Based Access Control**: Employee, Manager, and Admin roles with hierarchical permissions
- **Billing Rates**: Flexible rate management with fallback hierarchy (employee-project → project → employee → company)
- **Reports & Analytics**: Hours summary, utilization reports, and approval metrics
- **Out-of-Office Management**: Track and manage employee absences
- **Approval Delegation**: Managers can delegate approval authority
- **Audit Logging**: Complete audit trail for admin oversight

## Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Runtime |
| Django | 5.0+ | Web framework |
| Django REST Framework | 3.14+ | API layer |
| PostgreSQL | 15 | Database |
| Redis | 7 | Cache & message broker |
| Celery | 5.3+ | Background tasks |
| SimpleJWT | - | JWT authentication |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI framework |
| TypeScript | 5.9 | Type safety |
| Vite | 7.x | Build tool |
| TanStack Query | 5.x | Server state |
| TanStack Table | 8.x | Data tables |
| Zustand | 5.x | Client state |
| React Hook Form | 7.x | Forms |
| Tailwind CSS | 4.x | Styling |
| Radix UI | - | Accessible components |
| Recharts | 3.x | Charts |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Orchestration |
| Nginx | Frontend reverse proxy |
| Gunicorn | Python WSGI server |

## Project Structure

```
timetrack_pro/
├── apps/                          # Django applications
│   ├── users/                     # Authentication & user management
│   ├── companies/                 # Organization management
│   ├── projects/                  # Project management
│   ├── rates/                     # Billing rate management
│   ├── timeentries/               # Time entries & timer
│   ├── timesheets/                # Timesheet workflow
│   ├── reports/                   # Analytics & reporting
│   └── infrastructure/            # Shared utilities
├── config/                        # Django configuration
│   ├── settings/
│   │   ├── base.py               # Common settings
│   │   ├── development.py        # Development config
│   │   ├── production.py         # Production config
│   │   └── test.py               # Test config
│   ├── urls.py                   # URL routing
│   └── celery.py                 # Celery configuration
├── core/                          # Shared Django utilities
│   ├── models.py                 # Base model classes
│   ├── pagination.py             # DRF pagination
│   └── exceptions.py             # Exception handlers
├── frontend/                      # React application
│   ├── src/
│   │   ├── features/             # Feature modules
│   │   ├── components/           # Reusable components
│   │   ├── hooks/                # Custom hooks
│   │   ├── lib/                  # Utilities
│   │   ├── routes/               # Route configuration
│   │   └── types/                # TypeScript types
│   ├── Dockerfile                # Frontend container
│   └── nginx.conf                # Nginx configuration
├── Dockerfile                    # Backend container
├── docker-compose.yml            # Multi-container setup
├── requirements.txt              # Python dependencies
└── pyproject.toml                # Tool configuration
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/bomino/TimeAllocation.git
   cd TimeAllocation/timetrack_pro
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Seed demo data (optional)**
   ```bash
   docker-compose exec backend python manage.py seed_demo_data
   ```

6. **Access the application**
   - Frontend: http://localhost:3080
   - Backend API: http://localhost:8088/api/v1/
   - API Documentation: http://localhost:8088/api/docs/
   - Django Admin: http://localhost:8088/admin/

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Employee | john.doe@timetrack.local | demo123 |
| Manager | bob.manager@timetrack.local | demo123 |
| Admin | admin@timetrack.local | demo123 |

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3080 | React application |
| Backend | 8088 | Django API |
| PostgreSQL | 5440 | Database |
| Redis | 6400 | Cache/broker |
| PostgreSQL (test) | 5441 | Test database |

## Local Development

### Backend Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Set environment variables**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.development
   export DB_HOST=localhost
   export DB_PORT=5440
   export DB_NAME=timetrack_dev
   export DB_USER=postgres
   export DB_PASSWORD=postgres
   export REDIS_URL=redis://localhost:6400
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access at** http://localhost:5173

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login/` | POST | User login |
| `/api/v1/auth/logout/` | POST | User logout |
| `/api/v1/auth/refresh/` | POST | Refresh access token |
| `/api/v1/auth/password/reset/` | POST | Request password reset |
| `/api/v1/auth/password/reset/confirm/` | POST | Confirm password reset |

### Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/me/` | GET | Get current user profile |
| `/api/v1/users/<id>/deactivate/` | POST | Deactivate user (admin) |

### Projects

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/projects/` | GET | List projects |
| `/api/v1/projects/` | POST | Create project |
| `/api/v1/projects/<id>/` | GET | Get project details |
| `/api/v1/projects/<id>/` | PATCH | Update project |

### Time Entries

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/time-entries/` | GET | List time entries |
| `/api/v1/time-entries/` | POST | Create time entry |
| `/api/v1/time-entries/<id>/` | GET | Get entry details |
| `/api/v1/time-entries/<id>/` | PATCH | Update entry |
| `/api/v1/time-entries/<id>/` | DELETE | Delete entry |
| `/api/v1/time-entries/timer/start/` | POST | Start timer |
| `/api/v1/time-entries/timer/stop/` | POST | Stop timer |
| `/api/v1/time-entries/timer/active/` | GET | Get active timer |

### Timesheets

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/timesheets/` | GET | List timesheets |
| `/api/v1/timesheets/` | POST | Create timesheet |
| `/api/v1/timesheets/<id>/` | PATCH | Update/approve/reject |
| `/api/v1/timesheets/audit-log/` | GET | Admin audit log |

### Rates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rates/` | GET | List rates |
| `/api/v1/rates/` | POST | Create rate |
| `/api/v1/rates/effective/` | GET | Get effective rate |
| `/api/v1/rates/<id>/` | PATCH | Update rate |

### Reports

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/reports/hours/summary/` | GET | Hours summary |
| `/api/v1/reports/approval/metrics/` | GET | Approval metrics |
| `/api/v1/reports/utilization/` | GET | Utilization report |

## Authentication

TimeTrack Pro uses JWT (JSON Web Tokens) for authentication.

### Token Configuration

| Setting | Value |
|---------|-------|
| Access Token Lifetime | 8 hours |
| Refresh Token Lifetime | 7 days |
| Token Rotation | Enabled |
| Blacklist After Rotation | Yes |

### Using the API

Include the access token in the Authorization header:

```bash
curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8088/api/v1/time-entries/
```

### Refreshing Tokens

```bash
curl -X POST http://localhost:8088/api/v1/auth/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "<refresh_token>"}'
```

## User Roles

| Role | Permissions |
|------|-------------|
| **Employee** | Create/edit own time entries, submit timesheets |
| **Manager** | Employee permissions + approve team timesheets, view team reports |
| **Admin** | Full system access, user management, audit logs |

### Date Validation Rules

- **Employees**: Can enter time for current week + 1 week back
- **Admins**: Can enter time for current week + 1 month back

### Automatic Timesheet Creation

When a time entry is created, the system automatically:
1. Calculates the week start date based on the company's `week_start_day` setting
2. Creates a new timesheet for that week if one doesn't exist
3. Links the time entry to the timesheet

This ensures all time entries are properly associated with timesheets for the approval workflow.

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `timetrack_dev` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.development` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `ALLOWED_HOSTS` | Allowed hosts (production) | - |
| `CORS_ALLOWED_ORIGINS` | CORS origins (production) | - |

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=core

# Run specific app tests
pytest apps/timeentries/

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run linting
npm run lint

# Type checking
npm run build
```

## Code Quality

### Backend

```bash
# Linting
ruff check .

# Auto-fix
ruff check . --fix

# Type checking
mypy apps/ config/ core/
```

### Frontend

```bash
cd frontend

# ESLint
npm run lint
```

## Production Deployment

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Build Docker images
docker-compose -f docker-compose.prod.yml build
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `SECRET_KEY` with strong random value
- [ ] Set `ALLOWED_HOSTS` appropriately
- [ ] Configure `CORS_ALLOWED_ORIGINS`
- [ ] Use HTTPS
- [ ] Configure database backups
- [ ] Set up log aggregation
- [ ] Configure error tracking (Sentry recommended)

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/api/docs/`
- **OpenAPI Schema**: `/api/schema/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Backend: Follow PEP 8, enforced by Ruff
- Frontend: Follow ESLint configuration
- Use meaningful commit messages
- Write tests for new features

## License

This project is proprietary software. All rights reserved.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/bomino/TimeAllocation/issues) page.
