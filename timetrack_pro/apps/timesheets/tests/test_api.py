"""
Tests for Timesheet API endpoints - TDD approach.

Endpoints:
- GET    /api/v1/timesheets/
- GET    /api/v1/timesheets/:id/
- POST   /api/v1/timesheets/:id/submit/
- POST   /api/v1/timesheets/:id/approve/
- POST   /api/v1/timesheets/:id/reject/
- POST   /api/v1/timesheets/:id/unlock/
- GET    /api/v1/timesheets/:id/comments/
- POST   /api/v1/timesheets/:id/comments/
"""
from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from apps.timesheets.models import Timesheet


@pytest.mark.django_db
class TestListTimesheetsEndpoint:
    """Tests for GET /api/v1/timesheets/"""

    def test_list_own_timesheets_returns_200(self, authenticated_client, user):
        """
        Given: An authenticated user with timesheets
        When: GET /timesheets/
        Then: Returns 200 with user's timesheets
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 17))

        response = authenticated_client.get('/api/v1/timesheets/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2

    def test_list_only_returns_own_timesheets(
        self, authenticated_client, user, user_factory
    ):
        """
        Given: Multiple users with timesheets
        When: User A requests /timesheets/
        Then: Only User A's timesheets are returned
        """
        other_user = user_factory()

        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))
        Timesheet.objects.create(user=other_user, week_start=date(2024, 6, 10))

        response = authenticated_client.get('/api/v1/timesheets/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['user'] == user.id

    def test_list_timesheets_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /timesheets/
        Then: Returns 401 Unauthorized
        """
        response = api_client.get('/api/v1/timesheets/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_timesheets_filter_by_status(self, authenticated_client, user):
        """
        Given: Timesheets with different statuses
        When: GET /timesheets/?status=SUBMITTED
        Then: Only submitted timesheets returned
        """
        Timesheet.objects.create(
            user=user, week_start=date(2024, 6, 10), status=Timesheet.Status.DRAFT
        )
        Timesheet.objects.create(
            user=user, week_start=date(2024, 6, 17), status=Timesheet.Status.SUBMITTED
        )

        response = authenticated_client.get(
            '/api/v1/timesheets/',
            {'status': 'SUBMITTED'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['status'] == 'SUBMITTED'

    def test_manager_can_see_direct_reports_timesheets(
        self, authenticated_manager_client, user, manager
    ):
        """
        Given: A manager with direct reports
        When: GET /timesheets/?view=team
        Then: Returns timesheets of direct reports
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))

        response = authenticated_manager_client.get(
            '/api/v1/timesheets/',
            {'view': 'team'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) >= 1


@pytest.mark.django_db
class TestRetrieveTimesheetEndpoint:
    """Tests for GET /api/v1/timesheets/:id/"""

    def test_get_own_timesheet_returns_200(self, authenticated_client, user):
        """
        Given: An authenticated user with a timesheet
        When: GET /timesheets/:id/
        Then: Returns 200 with timesheet details
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        response = authenticated_client.get(f'/api/v1/timesheets/{timesheet.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == timesheet.id
        assert response.data['week_start'] == '2024-06-10'

    def test_get_timesheet_includes_entries(
        self, authenticated_client, user, project
    ):
        """
        Given: A timesheet with entries
        When: GET /timesheets/:id/
        Then: Response includes entries data
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )
        TimeEntry.objects.create(
            user=user,
            project=project,
            timesheet=timesheet,
            date=date(2024, 6, 10),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get(f'/api/v1/timesheets/{timesheet.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert 'entries' in response.data
        assert len(response.data['entries']) == 1

    def test_get_timesheet_includes_total_hours(
        self, authenticated_client, user, project
    ):
        """
        Given: A timesheet with multiple entries
        When: GET /timesheets/:id/
        Then: Response includes calculated total_hours
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )
        TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 11), hours=Decimal('7.50'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get(f'/api/v1/timesheets/{timesheet.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_hours'] == '15.50'

    def test_get_other_users_timesheet_returns_404(
        self, authenticated_client, user_factory
    ):
        """
        Given: User A authenticated
        When: GET /timesheets/:id/ for User B's timesheet
        Then: Returns 404
        """
        other_user = user_factory()
        timesheet = Timesheet.objects.create(
            user=other_user,
            week_start=date(2024, 6, 10),
        )

        response = authenticated_client.get(f'/api/v1/timesheets/{timesheet.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_manager_can_view_direct_reports_timesheet(
        self, authenticated_manager_client, user
    ):
        """
        Given: A manager viewing direct report's timesheet
        When: GET /timesheets/:id/
        Then: Returns 200 with timesheet details
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        response = authenticated_manager_client.get(f'/api/v1/timesheets/{timesheet.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSubmitTimesheetEndpoint:
    """Tests for POST /api/v1/timesheets/:id/submit/"""

    def test_submit_draft_timesheet_returns_200(
        self, authenticated_client, user, project
    ):
        """
        Given: A draft timesheet with entries
        When: POST /timesheets/:id/submit/
        Then: Returns 200 and status changes to SUBMITTED
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )
        TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/submit/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'SUBMITTED'

        timesheet.refresh_from_db()
        assert timesheet.status == Timesheet.Status.SUBMITTED
        assert timesheet.submitted_at is not None

    def test_submit_empty_timesheet_returns_400(self, authenticated_client, user):
        """
        Given: A draft timesheet with no entries
        When: POST /timesheets/:id/submit/
        Then: Returns 400 (cannot submit empty timesheet)
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/submit/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_already_submitted_returns_400(
        self, authenticated_client, user, project
    ):
        """
        Given: An already submitted timesheet
        When: POST /timesheets/:id/submit/
        Then: Returns 400
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )
        TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/submit/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_submit_other_users_timesheet(
        self, authenticated_client, user_factory, project
    ):
        """
        Given: User A authenticated
        When: POST /timesheets/:id/submit/ for User B's timesheet
        Then: Returns 404
        """
        from apps.timeentries.models import TimeEntry

        other_user = user_factory()
        timesheet = Timesheet.objects.create(
            user=other_user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )
        TimeEntry.objects.create(
            user=other_user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/submit/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestApproveTimesheetEndpoint:
    """Tests for POST /api/v1/timesheets/:id/approve/"""

    def test_manager_approve_submitted_timesheet_returns_200(
        self, authenticated_manager_client, user, manager
    ):
        """
        Given: A submitted timesheet from direct report
        When: Manager POST /timesheets/:id/approve/
        Then: Returns 200 and status changes to APPROVED
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/approve/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'APPROVED'

        timesheet.refresh_from_db()
        assert timesheet.status == Timesheet.Status.APPROVED
        assert timesheet.approved_at is not None
        assert timesheet.approved_by == manager

    def test_employee_cannot_approve_timesheet(self, authenticated_client, user):
        """
        Given: An employee (not manager)
        When: POST /timesheets/:id/approve/
        Then: Returns 403 Forbidden
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/approve/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_approve_draft_timesheet(
        self, authenticated_manager_client, user
    ):
        """
        Given: A draft timesheet
        When: Manager POST /timesheets/:id/approve/
        Then: Returns 400 (must be submitted first)
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/approve/'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_approve_other_teams_timesheet(
        self, authenticated_manager_client, user_factory
    ):
        """
        Given: A manager approving non-direct-report's timesheet
        When: POST /timesheets/:id/approve/
        Then: Returns 403 or 404
        """
        other_user = user_factory()
        timesheet = Timesheet.objects.create(
            user=other_user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/approve/'
        )

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestRejectTimesheetEndpoint:
    """Tests for POST /api/v1/timesheets/:id/reject/"""

    def test_manager_reject_with_comment_returns_200(
        self, authenticated_manager_client, user, manager
    ):
        """
        Given: A submitted timesheet
        When: Manager POST /timesheets/:id/reject/ with comment
        Then: Returns 200, status REJECTED, comment created
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/reject/',
            {'comment': 'Please fix the hours on Monday.'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'REJECTED'

        timesheet.refresh_from_db()
        assert timesheet.status == Timesheet.Status.REJECTED
        assert timesheet.comments.count() == 1
        assert timesheet.comments.first().author == manager

    def test_reject_without_comment_returns_400(
        self, authenticated_manager_client, user
    ):
        """
        Given: A submitted timesheet
        When: Manager POST /timesheets/:id/reject/ without comment
        Then: Returns 400 (comment required)
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/reject/',
            {},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_can_include_entry_specific_comment(
        self, authenticated_manager_client, user, project
    ):
        """
        Given: A submitted timesheet with entries
        When: Manager rejects with entry-specific comment
        Then: Comment is linked to specific entry
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )
        entry = TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'), rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/reject/',
            {
                'comment': '8 hours seems too high.',
                'entry_id': entry.id,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        comment = timesheet.comments.first()
        assert comment.entry == entry


@pytest.mark.django_db
class TestUnlockTimesheetEndpoint:
    """Tests for POST /api/v1/timesheets/:id/unlock/"""

    def test_admin_unlock_approved_timesheet_returns_200(
        self, authenticated_admin_client, user, admin
    ):
        """
        Given: An approved timesheet
        When: Admin POST /timesheets/:id/unlock/
        Then: Returns 200, status DRAFT, override recorded
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
            locked_at=timezone.now(),
        )

        response = authenticated_admin_client.post(
            f'/api/v1/timesheets/{timesheet.id}/unlock/',
            {'reason': 'Employee needs to correct an error.'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'DRAFT'

        timesheet.refresh_from_db()
        assert timesheet.status == Timesheet.Status.DRAFT
        assert timesheet.admin_overrides.count() == 1

    def test_unlock_without_reason_returns_400(
        self, authenticated_admin_client, user
    ):
        """
        Given: An approved timesheet
        When: Admin POST /timesheets/:id/unlock/ without reason
        Then: Returns 400 (reason required)
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.post(
            f'/api/v1/timesheets/{timesheet.id}/unlock/',
            {},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_admin_cannot_unlock(self, authenticated_manager_client, user):
        """
        Given: A manager (not admin)
        When: POST /timesheets/:id/unlock/
        Then: Returns 403 Forbidden
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/unlock/',
            {'reason': 'Test'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unlock_respects_unlock_window(
        self, authenticated_admin_client, user
    ):
        """
        Given: A timesheet approved beyond unlock window
        When: Admin POST /timesheets/:id/unlock/
        Then: Returns 400 (outside unlock window)
        """
        from datetime import timedelta

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 1, 1),
            status=Timesheet.Status.APPROVED,
            approved_at=timezone.now() - timedelta(days=30),
            locked_at=timezone.now() - timedelta(days=30),
        )

        response = authenticated_admin_client.post(
            f'/api/v1/timesheets/{timesheet.id}/unlock/',
            {'reason': 'Need to fix old timesheet.'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTimesheetCommentsEndpoint:
    """Tests for timesheet comments endpoints."""

    def test_list_comments_returns_200(self, authenticated_client, user, manager):
        """
        Given: A timesheet with comments
        When: GET /timesheets/:id/comments/
        Then: Returns 200 with comments list
        """
        from apps.timesheets.models import TimesheetComment

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )
        TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='First comment',
        )
        TimesheetComment.objects.create(
            timesheet=timesheet,
            author=user,
            text='Response',
        )

        response = authenticated_client.get(f'/api/v1/timesheets/{timesheet.id}/comments/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_add_comment_to_own_timesheet(self, authenticated_client, user):
        """
        Given: A rejected timesheet
        When: Owner POST /timesheets/:id/comments/
        Then: Returns 201 and comment is added
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.REJECTED,
        )

        response = authenticated_client.post(
            f'/api/v1/timesheets/{timesheet.id}/comments/',
            {'text': 'I have fixed the hours.'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert timesheet.comments.count() == 1

    def test_manager_can_add_comment(
        self, authenticated_manager_client, user, manager
    ):
        """
        Given: A direct report's timesheet
        When: Manager POST /timesheets/:id/comments/
        Then: Returns 201 and comment is added
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/comments/',
            {'text': 'Please clarify.'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert timesheet.comments.first().author == manager

    def test_add_comment_without_text_returns_400(
        self, authenticated_client, user
    ):
        """
        Given: A timesheet
        When: POST /timesheets/:id/comments/ without text
        Then: Returns 400
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        response = authenticated_client.post(
            f'/api/v1/timesheets/{timesheet.id}/comments/',
            {},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
