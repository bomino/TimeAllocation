"""
Tests for User model.

Following TDD: Write tests first, then implement.
"""
import pytest
from django.db import IntegrityError


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""

    def test_user_creation_with_required_fields(self, user_factory):
        """User can be created with required fields."""
        user = user_factory(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )

        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'

    def test_user_default_role_is_employee(self, user_factory):
        """New users default to EMPLOYEE role."""
        from apps.users.models import User

        user = user_factory()

        assert user.role == User.Role.EMPLOYEE

    def test_user_can_have_manager(self, user_factory):
        """User can have a manager assigned."""
        from apps.users.models import User

        manager = user_factory(role=User.Role.MANAGER)
        employee = user_factory(manager=manager)

        assert employee.manager == manager
        assert employee.manager.role == User.Role.MANAGER

    def test_user_manager_can_be_null(self, user_factory):
        """User manager can be null (for top-level managers/admins)."""
        user = user_factory(manager=None)

        assert user.manager is None

    def test_user_default_timezone_is_utc(self, user_factory):
        """New users default to UTC timezone."""
        user = user_factory()

        assert user.timezone == 'UTC'

    def test_user_notification_preferences_default_to_true(self, user_factory):
        """Notification preferences default to enabled."""
        user = user_factory()

        assert user.workflow_notifications_enabled is True
        assert user.security_notifications_enabled is True

    def test_user_belongs_to_company(self, user_factory, company):
        """User must belong to a company."""
        user = user_factory(company=company)

        assert user.company == company

    def test_user_str_returns_full_name(self, user_factory):
        """User string representation returns full name."""
        user = user_factory(first_name='John', last_name='Doe')

        assert str(user) == 'John Doe'

    def test_user_get_full_name(self, user_factory):
        """get_full_name() returns first and last name."""
        user = user_factory(first_name='Jane', last_name='Smith')

        assert user.get_full_name() == 'Jane Smith'

    def test_user_email_is_unique(self, user_factory):
        """Email addresses must be unique."""
        user_factory(email='unique@example.com')

        with pytest.raises(IntegrityError):
            user_factory(email='unique@example.com')

    def test_user_role_choices(self, user_factory):
        """User role must be one of the defined choices."""
        from apps.users.models import User

        employee = user_factory(role=User.Role.EMPLOYEE)
        manager = user_factory(role=User.Role.MANAGER)
        admin = user_factory(role=User.Role.ADMIN)

        assert employee.role == 'EMPLOYEE'
        assert manager.role == 'MANAGER'
        assert admin.role == 'ADMIN'

    def test_user_has_timestamps(self, user_factory):
        """User has created_at and updated_at timestamps."""
        user = user_factory()

        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_is_manager_property(self, user_factory):
        """is_manager property returns True for managers."""
        from apps.users.models import User

        employee = user_factory(role=User.Role.EMPLOYEE)
        manager = user_factory(role=User.Role.MANAGER)
        admin = user_factory(role=User.Role.ADMIN)

        assert employee.is_manager is False
        assert manager.is_manager is True
        assert admin.is_manager is True  # Admins can also approve

    def test_user_is_admin_property(self, user_factory):
        """is_admin property returns True only for admins."""
        from apps.users.models import User

        employee = user_factory(role=User.Role.EMPLOYEE)
        manager = user_factory(role=User.Role.MANAGER)
        admin = user_factory(role=User.Role.ADMIN)

        assert employee.is_admin is False
        assert manager.is_admin is False
        assert admin.is_admin is True
