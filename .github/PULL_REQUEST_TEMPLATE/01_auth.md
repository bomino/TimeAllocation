# Slice 1: Auth + Profile

## Summary

<!-- Brief description of what this PR implements -->

## Changes

- [ ] User model (extends AbstractUser)
- [ ] Company model
- [ ] CompanySettings model with audit log
- [ ] JWT authentication endpoints
- [ ] Password reset flow
- [ ] User profile endpoints

## Checklist

### Endpoints Working

- [ ] `POST /api/v1/auth/login/` - Returns access + refresh tokens
- [ ] `POST /api/v1/auth/logout/` - Blacklists refresh token
- [ ] `POST /api/v1/auth/refresh/` - Refreshes access token
- [ ] `POST /api/v1/auth/password/reset/` - Sends reset email (mocked)
- [ ] `POST /api/v1/auth/password/reset/confirm/` - Completes reset
- [ ] `GET /api/v1/users/me/` - Returns current user profile
- [ ] `PUT /api/v1/users/me/` - Updates current user profile

### Test Coverage

- [ ] **401 Tests**: All endpoints reject unauthenticated requests
- [ ] **403 Tests**: Employee cannot view/edit other users' profiles
- [ ] **Happy Path Tests**: Login, logout, refresh, reset flow
- [ ] **Edge Cases**: Invalid credentials, locked account, expired token
- [ ] **100% coverage** on `apps/users/models.py`
- [ ] **100% coverage** on `apps/companies/models.py`

### Database

- [ ] Migrations committed and applied cleanly
- [ ] All tests pass with PostgreSQL (not SQLite)
- [ ] Indexes added on foreign keys

### Code Quality

- [ ] `ruff check .` passes
- [ ] `ruff format .` passes
- [ ] `mypy apps/` passes (or explicit ignores documented)
- [ ] No `# type: ignore` without explanation
- [ ] No `as any`, `@ts-ignore` equivalents

### Documentation

- [ ] API endpoints documented in code (docstrings or OpenAPI)
- [ ] ADR written if any significant decisions made
- [ ] Factory fixtures created for users, companies

## Testing Instructions

```bash
# Run slice tests
pytest apps/users/ apps/companies/ -v

# Check coverage
pytest apps/users/ apps/companies/ --cov=apps/users --cov=apps/companies --cov-report=term-missing

# Manual test
# 1. Start server: python manage.py runserver
# 2. POST /api/v1/auth/login/ with valid credentials
# 3. Verify tokens returned
# 4. GET /api/v1/users/me/ with Bearer token
```

## Related Issues

<!-- Link to any related issues or tickets -->

---

**Slice Status:** Auth + Profile (Fixed boundary - no scope changes)
