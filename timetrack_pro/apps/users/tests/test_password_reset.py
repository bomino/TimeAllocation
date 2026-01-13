"""
Tests for Password Reset API endpoints - TDD approach.

Endpoints:
- POST /api/v1/auth/password/reset/
- POST /api/v1/auth/password/reset/confirm/
"""
import pytest
from unittest.mock import patch
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@pytest.mark.django_db
class TestPasswordResetRequestEndpoint:
    """Tests for POST /api/v1/auth/password/reset/"""

    @patch('apps.users.views.send_password_reset_email.delay')
    def test_password_reset_request_with_valid_email(self, mock_send, api_client, user):
        """
        Given: A registered user email
        When: POST /auth/password/reset/
        Then: Returns 200 and queues email task
        """
        response = api_client.post('/api/v1/auth/password/reset/', {
            'email': user.email,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        mock_send.assert_called_once()

    def test_password_reset_request_with_nonexistent_email_returns_200(self, api_client):
        """
        Given: An unregistered email
        When: POST /auth/password/reset/
        Then: Returns 200 (for security - don't reveal if email exists)
        """
        response = api_client.post('/api/v1/auth/password/reset/', {
            'email': 'nonexistent@example.com',
        })

        # Always return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_request_without_email_returns_400(self, api_client):
        """
        Given: Missing email field
        When: POST /auth/password/reset/
        Then: Returns 400 Bad Request
        """
        response = api_client.post('/api/v1/auth/password/reset/', {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_request_with_invalid_email_format(self, api_client):
        """
        Given: Invalid email format
        When: POST /auth/password/reset/
        Then: Returns 400 Bad Request
        """
        response = api_client.post('/api/v1/auth/password/reset/', {
            'email': 'not-an-email',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.users.views.send_password_reset_email.delay')
    def test_password_reset_request_for_inactive_user_returns_200(
        self, mock_send, api_client, user_factory
    ):
        """
        Given: An inactive user
        When: POST /auth/password/reset/
        Then: Returns 200 but doesn't send email
        """
        inactive_user = user_factory(is_active=False)

        response = api_client.post('/api/v1/auth/password/reset/', {
            'email': inactive_user.email,
        })

        assert response.status_code == status.HTTP_200_OK
        mock_send.assert_not_called()


@pytest.mark.django_db
class TestPasswordResetConfirmEndpoint:
    """Tests for POST /api/v1/auth/password/reset/confirm/"""

    @patch('apps.users.views.send_password_changed_notification.delay')
    def test_password_reset_confirm_with_valid_token(self, mock_notify, api_client, user):
        """
        Given: Valid uid and token
        When: POST /auth/password/reset/confirm/ with new password
        Then: Returns 200 and password is changed
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        new_password = 'NewSecurePass123!'

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': new_password,
            'confirm_password': new_password,
        })

        assert response.status_code == status.HTTP_200_OK

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_password_reset_confirm_with_invalid_token(self, api_client, user):
        """
        Given: Invalid token
        When: POST /auth/password/reset/confirm/
        Then: Returns 400 Bad Request
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': 'invalid-token',
            'new_password': 'NewSecurePass123!',
            'confirm_password': 'NewSecurePass123!',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_with_invalid_uid(self, api_client, user):
        """
        Given: Invalid uid
        When: POST /auth/password/reset/confirm/
        Then: Returns 400 Bad Request
        """
        token = default_token_generator.make_token(user)

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': 'invalid-uid',
            'token': token,
            'new_password': 'NewSecurePass123!',
            'confirm_password': 'NewSecurePass123!',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_mismatched_passwords(self, api_client, user):
        """
        Given: Passwords don't match
        When: POST /auth/password/reset/confirm/
        Then: Returns 400 Bad Request
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'NewSecurePass123!',
            'confirm_password': 'DifferentPass123!',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_weak_password(self, api_client, user):
        """
        Given: Weak password that fails Django validators
        When: POST /auth/password/reset/confirm/
        Then: Returns 400 Bad Request
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': '123',
            'confirm_password': '123',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_missing_fields(self, api_client):
        """
        Given: Missing required fields
        When: POST /auth/password/reset/confirm/
        Then: Returns 400 Bad Request
        """
        response = api_client.post('/api/v1/auth/password/reset/confirm/', {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.users.views.send_password_changed_notification.delay')
    def test_password_reset_invalidates_token_after_use(self, mock_notify, api_client, user):
        """
        Given: Valid uid and token (already used)
        When: POST /auth/password/reset/confirm/ again
        Then: Returns 400 (token invalid after password change)
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        new_password = 'NewSecurePass123!'

        # First request succeeds
        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': new_password,
            'confirm_password': new_password,
        })
        assert response.status_code == status.HTTP_200_OK

        # Second request with same token fails
        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'AnotherPass456!',
            'confirm_password': 'AnotherPass456!',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('apps.users.views.send_password_changed_notification.delay')
    def test_password_reset_confirm_sends_notification(self, mock_notify, api_client, user):
        """
        Given: User has security notifications enabled
        When: Password is reset successfully
        Then: Security notification is queued
        """
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = api_client.post('/api/v1/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password': 'NewSecurePass123!',
            'confirm_password': 'NewSecurePass123!',
        })

        assert response.status_code == status.HTTP_200_OK
        mock_notify.assert_called_once_with(user.id)
