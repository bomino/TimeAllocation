# ADR-XXXX: [Short Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Author:** [Name]

---

## Problem

[Describe the problem or question that needs a decision. What is the context? What constraints exist?]

## Decision

[State the decision that was made. Be specific and actionable.]

## Rationale

[Explain why this decision was made. What alternatives were considered? What trade-offs were accepted?]

## Consequences

[Describe the implications of this decision. Include both positive outcomes and any risks or technical debt introduced.]

---

## Example: ADR-0002

Below is an example of a completed ADR.

---

# ADR-0002: Use Injected Clock Service for Time Operations

**Status:** Accepted
**Date:** 2024-01-15
**Author:** TimeTrack Pro Team

---

## Problem

Time-dependent business logic (escalation after N days, rate effective dates, timesheet week boundaries) is difficult to test reliably. Using `datetime.now()` directly makes tests non-deterministic and requires complex mocking.

## Decision

Implement a `Clock` protocol with two implementations:
- `SystemClock` for production (returns actual system time)
- `TestClock` for testing (supports `now()`, `travel_to()`, `advance()`)

Inject the clock via dependency injection into services and views that need current time.

## Rationale

**Alternatives considered:**

1. **freezegun library** - Works but requires decorator/context manager on every test. Global time mutation can cause subtle issues with parallel tests.

2. **Mocking datetime.now()** - Fragile, doesn't work well across module boundaries, and becomes complex with multiple time sources.

3. **Injected clock (chosen)** - Explicit dependency, easy to test, follows dependency inversion principle. Slightly more code but much clearer intent.

**Trade-offs accepted:**
- Extra parameter threading through code
- Slightly more setup in tests

## Consequences

**Positive:**
- All time-dependent tests are deterministic
- Can test edge cases like DST transitions, month/year boundaries
- Clear separation between "get current time" and "format time"

**Negative:**
- Every service/view that needs time must accept clock parameter
- Need to remember to use clock instead of datetime.now()

**Mitigations:**
- Add lint rule to flag direct datetime.now() usage
- Code review checklist item for new time-dependent code
