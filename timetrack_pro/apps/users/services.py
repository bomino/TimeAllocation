"""
Services for User business logic.

Includes:
- DeactivationService: Handles user deactivation with data export
"""
import base64
import csv
import io
from typing import Any

from apps.timesheets.models import Timesheet
from apps.users.models import User, UserDeactivationAudit


class DeactivationService:
    """
    Service for handling user deactivation.

    Business Rules:
    - Cannot deactivate user with pending timesheets (DRAFT or SUBMITTED)
    - Admin can force deactivate, overriding pending check
    - All user data is exported (JSON + CSV) before deactivation
    - Export stored in UserDeactivationAudit for compliance
    """

    @classmethod
    def can_deactivate(cls, user: User) -> bool:
        """
        Check if a user can be deactivated.

        Args:
            user: The user to check

        Returns:
            True if no pending timesheets, False otherwise
        """
        return cls.get_pending_timesheets_count(user) == 0

    @classmethod
    def get_pending_timesheets_count(cls, user: User) -> int:
        """
        Get count of pending timesheets (DRAFT + SUBMITTED).

        Args:
            user: The user to check

        Returns:
            Count of pending timesheets
        """
        return Timesheet.objects.filter(
            user=user,
            status__in=[Timesheet.Status.DRAFT, Timesheet.Status.SUBMITTED],
        ).count()

    @classmethod
    def export_user_data(cls, user: User) -> dict[str, Any]:
        """
        Export all user data for archival.

        Args:
            user: The user to export

        Returns:
            Dict with profile, time_entries, timesheets, and csv_blob
        """
        from apps.timeentries.models import TimeEntry

        profile = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'timezone': user.timezone,
            'company_id': user.company_id,
            'manager_id': user.manager_id,
            'date_joined': str(user.date_joined),
        }

        time_entries = list(
            TimeEntry.objects.filter(user=user).values(
                'id',
                'project_id',
                'date',
                'hours',
                'description',
                'billing_rate',
                'rate_source',
                'created_at',
            )
        )
        for entry in time_entries:
            entry['date'] = str(entry['date'])
            entry['hours'] = str(entry['hours'])
            entry['billing_rate'] = str(entry['billing_rate'])
            entry['created_at'] = str(entry['created_at'])

        timesheets = list(
            Timesheet.objects.filter(user=user).values(
                'id',
                'week_start',
                'status',
                'submitted_at',
                'approved_at',
                'approved_by_id',
                'created_at',
            )
        )
        for ts in timesheets:
            ts['week_start'] = str(ts['week_start'])
            ts['submitted_at'] = str(ts['submitted_at']) if ts['submitted_at'] else None
            ts['approved_at'] = str(ts['approved_at']) if ts['approved_at'] else None
            ts['created_at'] = str(ts['created_at'])

        csv_blob = cls._create_csv_blob(user, time_entries)

        return {
            'profile': profile,
            'time_entries': time_entries,
            'timesheets': timesheets,
            'csv_blob': csv_blob,
        }

    @classmethod
    def _create_csv_blob(cls, user: User, time_entries: list[dict]) -> str:
        """
        Create base64-encoded CSV of time entries.

        Args:
            user: The user
            time_entries: List of time entry dicts

        Returns:
            Base64-encoded CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'date',
            'project_id',
            'hours',
            'description',
            'billing_rate',
            'rate_source',
        ])

        for entry in time_entries:
            writer.writerow([
                entry['date'],
                entry['project_id'],
                entry['hours'],
                entry.get('description', ''),
                entry['billing_rate'],
                entry['rate_source'],
            ])

        csv_content = output.getvalue()
        return base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')

    @classmethod
    def execute_deactivation(
        cls,
        user: User,
        admin: User,
        reason: str,
        force: bool = False,
    ) -> UserDeactivationAudit:
        """
        Execute user deactivation with data export.

        Args:
            user: The user to deactivate
            admin: The admin performing deactivation
            reason: Reason for deactivation
            force: Override pending timesheets check

        Returns:
            UserDeactivationAudit record

        Raises:
            ValueError: If user has pending timesheets and force=False
        """
        pending_count = cls.get_pending_timesheets_count(user)

        if pending_count > 0 and not force:
            raise ValueError(
                f'User has {pending_count} pending timesheets. '
                'Resolve them first or use force=True to override.'
            )

        export_data = cls.export_user_data(user)

        audit = UserDeactivationAudit.objects.create(
            user=user,
            admin=admin,
            reason=reason,
            was_forced=force and pending_count > 0,
            pending_timesheets_at_deactivation=pending_count,
            export_data=export_data,
        )

        user.is_active = False
        user.save()

        return audit
