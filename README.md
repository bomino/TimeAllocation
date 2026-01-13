# TimeAllocation

Employee time allocation and timesheet management system.

## Projects

### [TimeTrack Pro](./timetrack_pro/)

A comprehensive time tracking application built with Django REST Framework and React.

**Features:**
- Time entry tracking with optional timer
- Timesheet submission and approval workflow
- Role-based access control (Employee, Manager, Admin)
- Billing rate management
- Reports and analytics
- Out-of-office management

**Tech Stack:**
- Backend: Python 3.12, Django 5.0+, PostgreSQL, Redis, Celery
- Frontend: React 19, TypeScript, Vite, TanStack Query, Tailwind CSS
- Infrastructure: Docker, Nginx, Gunicorn

**Quick Start:**
```bash
cd timetrack_pro
docker-compose up -d
```

See [timetrack_pro/README.md](./timetrack_pro/README.md) for detailed documentation.

## Documentation

- [PRD1.md](./PRD1.md) - Initial product requirements
- [PRD2.md](./PRD2.md) - Extended product requirements
- [PM-PRD1.md](./PM-PRD1.md) - Project management PRD
- [docs/](./docs/) - Additional documentation

## License

Proprietary software. All rights reserved.
