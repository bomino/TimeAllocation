# Slice 3: Timesheet + Approval

## Summary

<!-- Brief description of what this PR implements -->

## Changes

- [ ] Timesheet model with status workflow
- [ ] TimesheetComment model with mentions
- [ ] OOOPeriod model
- [ ] AdminOverride model with export blob
- [ ] Weekly timesheet auto-creation (Celery task)
- [ ] Approval chain with escalation
- [ ] Line-item conversation on rejection

## Checklist

### Endpoints Working

- [ ] `GET /api/v1/timesheets/` - List user's timesheets
- [ ] `GET /api/v1/timesheets/:id/` - Get timesheet details with entries
- [ ] `POST /api/v1/timesheets/:id/submit/` - Submit for approval
- [ ] `POST /api/v1/timesheets/:id/approve/` - Approve (manager)
- [ ] `POST /api/v1/timesheets/:id/reject/` - Reject with comments (manager)
- [ ] `POST /api/v1/timesheets/:id/unlock/` - Unlock (admin only)
- [ ] `GET /api/v1/timesheets/:id/comments/` - List comments
- [ ] `POST /api/v1/timesheets/:id/comments/` - Add comment

### Business Logic Tests

#### Timesheet Lifecycle
- [ ] Auto-created weekly via Celery cron
- [ ] Week boundary respects company's week_start_day
- [ ] Timesheet created in company timezone
- [ ] Cannot submit partial week (full week only)
- [ ] Cannot submit empty timesheet (BIZ_004)

#### Approval Workflow
- [ ] Submit changes status to SUBMITTED
- [ ] Primary manager can approve
- [ ] Non-manager cannot approve (403)
- [ ] Manager cannot approve non-direct-report (403)
- [ ] Approval sets approved_at and approved_by
- [ ] Approval locks timesheet

#### Rejection Flow
- [ ] Reject changes status to REJECTED
- [ ] Rejection requires at least one comment
- [ ] Comments can target specific entries
- [ ] Employee can resubmit after rejection
- [ ] Conversation history collapsed on approval

#### Escalation
- [ ] Escalation triggered by OOO OR pending X days (configurable)
- [ ] Escalation notifies next manager in chain
- [ ] Chain terminus notifies admin
- [ ] Escalation respects AND/OR company setting

#### Unlock (Admin)
- [ ] Only admin can unlock approved timesheet
- [ ] Unlock requires reason
- [ ] Unlock within configurable window
- [ ] AdminOverride audit record created
- [ ] Previous state captured in audit

#### OOO Periods
- [ ] Can have 1 active + 1 future OOO period
- [ ] Cannot create overlapping periods beyond limit
- [ ] OOO triggers escalation when combined with pending

### Celery Tasks

- [ ] `create_weekly_timesheets` task works
- [ ] `check_escalations` task works
- [ ] Tasks tested via mocking task.delay()
- [ ] Notifications queued correctly

### Test Coverage

- [ ] **403 Tests**: Permission matrix for all roles
- [ ] **100% coverage** on `apps/timesheets/models.py`
- [ ] **100% coverage** on `apps/timesheets/services.py`
- [ ] **Escalation edge cases**: OOO only, days only, both, chain terminus

### Database

- [ ] Migrations committed and applied cleanly
- [ ] All tests pass with PostgreSQL
- [ ] Unique constraint on (user, week_start)

### Code Quality

- [ ] `ruff check .` passes
- [ ] `ruff format .` passes
- [ ] `mypy apps/` passes
- [ ] Clock service used for all time operations

### Documentation

- [ ] Approval workflow documented
- [ ] Escalation logic documented
- [ ] ADR written for any significant decisions
- [ ] Factory fixtures created for timesheets, comments, OOO periods

## Testing Instructions

```bash
# Run slice tests
pytest apps/timesheets/ -v

# Check coverage
pytest apps/timesheets/ --cov=apps/timesheets --cov-report=term-missing

# Test approval workflow manually
# 1. Login as employee
# 2. Create time entries for current week
# 3. POST /timesheets/:id/submit/
# 4. Login as manager
# 5. POST /timesheets/:id/approve/
# 6. Verify timesheet locked

# Test escalation manually
# 1. Create submitted timesheet
# 2. Set manager to OOO
# 3. Advance clock 3+ days
# 4. Trigger check_escalations task
# 5. Verify escalation occurred
```

## Related Issues

<!-- Link to any related issues or tickets -->

---

**Slice Status:** Timesheet + Approval (Boundary may be refined based on earlier slices)
