# Slice 2: Time Entry + Timer

## Summary

<!-- Brief description of what this PR implements -->

## Changes

- [ ] Project model
- [ ] Rate model with hierarchy support
- [ ] TimeEntry model with rate snapshotting
- [ ] Rate resolution service
- [ ] Timer start/stop functionality
- [ ] Daily hour limit validation

## Checklist

### Endpoints Working

- [ ] `GET /api/v1/time-entries/` - List user's entries
- [ ] `POST /api/v1/time-entries/` - Create entry (snapshots rate)
- [ ] `GET /api/v1/time-entries/:id/` - Get entry details
- [ ] `PUT /api/v1/time-entries/:id/` - Update entry (rate immutable)
- [ ] `DELETE /api/v1/time-entries/:id/` - Delete entry
- [ ] `POST /api/v1/time-entries/timer/start/` - Start timer
- [ ] `POST /api/v1/time-entries/timer/stop/` - Stop timer
- [ ] `GET /api/v1/rates/effective/:userId/:projectId/` - Get effective rate

### Business Logic Tests

#### Rate Resolution
- [ ] Employee-project rate takes priority
- [ ] Project rate used when no employee-project rate
- [ ] Employee rate used when no project rate
- [ ] Company default used as final fallback
- [ ] Expired rates (effective_to in past) not used
- [ ] Future rates (effective_from in future) not used
- [ ] Rate effective date boundaries respected

#### Rate Snapshotting
- [ ] Rate captured at entry creation time
- [ ] Snapshot includes rate value and source
- [ ] Rate cannot be modified after creation
- [ ] Update endpoint does not change billing_rate

#### Timer
- [ ] Starting timer creates entry with timer_started_at
- [ ] Cannot start new timer when one is active (BIZ_005)
- [ ] Stopping timer calculates hours correctly
- [ ] Stopping timer snapshots current rate

#### Daily Limits
- [ ] Entry exceeding 24h for day is blocked (BIZ_003)
- [ ] Warning returned when approaching threshold
- [ ] Threshold respects hierarchical override (company → project → employee)

### Test Coverage

- [ ] **403 Tests**: Employee cannot view/edit other users' entries
- [ ] **100% coverage** on `apps/rates/models.py`
- [ ] **100% coverage** on `apps/rates/services.py`
- [ ] **100% coverage** on `apps/timeentries/models.py`
- [ ] **100% coverage** on `apps/projects/models.py`

### Database

- [ ] Migrations committed and applied cleanly
- [ ] All tests pass with PostgreSQL
- [ ] Indexes on (user, date) and (project, date)

### Code Quality

- [ ] `ruff check .` passes
- [ ] `ruff format .` passes
- [ ] `mypy apps/` passes
- [ ] Clock service injected (no direct datetime.now())

### Documentation

- [ ] Rate resolution algorithm documented
- [ ] ADR written for any significant decisions
- [ ] Factory fixtures created for projects, rates, time entries

## Testing Instructions

```bash
# Run slice tests
pytest apps/projects/ apps/rates/ apps/timeentries/ -v

# Check coverage
pytest apps/rates/ --cov=apps/rates --cov-report=term-missing

# Test rate resolution manually
# 1. Create company with default rate $50
# 2. Create project
# 3. Create employee-project rate $100
# 4. POST time entry, verify billing_rate = $100
# 5. Delete employee-project rate
# 6. POST time entry, verify billing_rate = $50 (fallback)
```

## Related Issues

<!-- Link to any related issues or tickets -->

---

**Slice Status:** Time Entry + Timer (Boundary may be refined based on Slice 1 learnings)
