"""
Tests for Rate Management API - TDD approach.

Endpoints:
- GET    /api/v1/rates/
- POST   /api/v1/rates/
- GET    /api/v1/rates/:id/
- PUT    /api/v1/rates/:id/
- DELETE /api/v1/rates/:id/
- GET    /api/v1/rates/effective/ (resolve rate for user/project)
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework import status

from apps.rates.models import Rate


@pytest.mark.django_db
class TestListRatesEndpoint:
    """Tests for GET /api/v1/rates/"""

    def test_admin_can_list_company_rates(
        self, authenticated_admin_client, company, rate_factory
    ):
        """
        Given: Admin with company rates
        When: GET /rates/
        Then: Returns 200 with company rates
        """
        rate_factory(company=company, rate_type=Rate.RateType.PROJECT)
        rate_factory(company=company, rate_type=Rate.RateType.EMPLOYEE)

        response = authenticated_admin_client.get('/api/v1/rates/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2

    def test_manager_can_list_company_rates(
        self, authenticated_manager_client, company, rate_factory
    ):
        """
        Given: Manager in company with rates
        When: GET /rates/
        Then: Returns 200 with company rates
        """
        rate_factory(company=company, rate_type=Rate.RateType.PROJECT)

        response = authenticated_manager_client.get('/api/v1/rates/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_employee_cannot_list_rates(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /rates/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/rates/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_rates_by_type(
        self, authenticated_admin_client, company, rate_factory
    ):
        """
        Given: Rates of different types
        When: GET /rates/?rate_type=PROJECT
        Then: Only PROJECT rates returned
        """
        rate_factory(company=company, rate_type=Rate.RateType.PROJECT)
        rate_factory(company=company, rate_type=Rate.RateType.EMPLOYEE)

        response = authenticated_admin_client.get('/api/v1/rates/?rate_type=PROJECT')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['rate_type'] == Rate.RateType.PROJECT

    def test_filter_rates_by_employee(
        self, authenticated_admin_client, company, user, rate_factory
    ):
        """
        Given: Rates for different employees
        When: GET /rates/?employee_id=:id
        Then: Only that employee's rates returned
        """
        rate_factory(company=company, employee=user, rate_type=Rate.RateType.EMPLOYEE)
        rate_factory(company=company, employee=None, rate_type=Rate.RateType.PROJECT)

        response = authenticated_admin_client.get(f'/api/v1/rates/?employee_id={user.id}')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /rates/
        Then: Returns 401
        """
        response = api_client.get('/api/v1/rates/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreateRateEndpoint:
    """Tests for POST /api/v1/rates/"""

    def test_admin_can_create_project_rate(
        self, authenticated_admin_client, company, project
    ):
        """
        Given: Admin user
        When: POST /rates/ with PROJECT rate
        Then: Returns 201 with created rate
        """
        payload = {
            'project_id': project.id,
            'rate_type': Rate.RateType.PROJECT,
            'hourly_rate': '150.00',
            'effective_from': str(date.today()),
        }

        response = authenticated_admin_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rate.objects.filter(project=project).exists()

    def test_admin_can_create_employee_rate(
        self, authenticated_admin_client, company, user
    ):
        """
        Given: Admin user
        When: POST /rates/ with EMPLOYEE rate
        Then: Returns 201 with created rate
        """
        payload = {
            'employee_id': user.id,
            'rate_type': Rate.RateType.EMPLOYEE,
            'hourly_rate': '125.00',
            'effective_from': str(date.today()),
        }

        response = authenticated_admin_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rate.objects.filter(employee=user).exists()

    def test_admin_can_create_employee_project_rate(
        self, authenticated_admin_client, company, user, project
    ):
        """
        Given: Admin user
        When: POST /rates/ with EMPLOYEE_PROJECT rate
        Then: Returns 201 with created rate
        """
        payload = {
            'employee_id': user.id,
            'project_id': project.id,
            'rate_type': Rate.RateType.EMPLOYEE_PROJECT,
            'hourly_rate': '175.00',
            'effective_from': str(date.today()),
        }

        response = authenticated_admin_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Rate.objects.filter(employee=user, project=project).exists()

    def test_manager_cannot_create_rates(
        self, authenticated_manager_client, project
    ):
        """
        Given: Manager user (not admin)
        When: POST /rates/
        Then: Returns 403 Forbidden
        """
        payload = {
            'project_id': project.id,
            'rate_type': Rate.RateType.PROJECT,
            'hourly_rate': '150.00',
            'effective_from': str(date.today()),
        }

        response = authenticated_manager_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_rate_requires_hourly_rate(
        self, authenticated_admin_client, project
    ):
        """
        Given: Admin user
        When: POST /rates/ without hourly_rate
        Then: Returns 400
        """
        payload = {
            'project_id': project.id,
            'rate_type': Rate.RateType.PROJECT,
            'effective_from': str(date.today()),
        }

        response = authenticated_admin_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_rate_validates_effective_dates(
        self, authenticated_admin_client, project
    ):
        """
        Given: Admin user
        When: POST with effective_to before effective_from
        Then: Returns 400
        """
        payload = {
            'project_id': project.id,
            'rate_type': Rate.RateType.PROJECT,
            'hourly_rate': '150.00',
            'effective_from': str(date.today()),
            'effective_to': str(date.today() - timedelta(days=1)),
        }

        response = authenticated_admin_client.post('/api/v1/rates/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdateRateEndpoint:
    """Tests for PUT /api/v1/rates/:id/"""

    def test_admin_can_update_rate(
        self, authenticated_admin_client, rate_factory, company
    ):
        """
        Given: Existing rate
        When: PUT /rates/:id/ with new hourly_rate
        Then: Returns 200 with updated rate
        """
        rate = rate_factory(company=company, hourly_rate=Decimal('100.00'))

        payload = {
            'hourly_rate': '125.00',
            'effective_from': str(rate.effective_from),
            'rate_type': rate.rate_type,
        }

        response = authenticated_admin_client.put(f'/api/v1/rates/{rate.id}/', payload)

        assert response.status_code == status.HTTP_200_OK
        rate.refresh_from_db()
        assert rate.hourly_rate == Decimal('125.00')

    def test_manager_cannot_update_rates(
        self, authenticated_manager_client, rate_factory, company
    ):
        """
        Given: Manager user
        When: PUT /rates/:id/
        Then: Returns 403
        """
        rate = rate_factory(company=company)

        payload = {'hourly_rate': '125.00'}

        response = authenticated_manager_client.put(f'/api/v1/rates/{rate.id}/', payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDeleteRateEndpoint:
    """Tests for DELETE /api/v1/rates/:id/"""

    def test_admin_can_delete_rate(
        self, authenticated_admin_client, rate_factory, company
    ):
        """
        Given: Existing rate
        When: DELETE /rates/:id/
        Then: Returns 204 and rate is deleted
        """
        rate = rate_factory(company=company)

        response = authenticated_admin_client.delete(f'/api/v1/rates/{rate.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Rate.objects.filter(id=rate.id).exists()

    def test_manager_cannot_delete_rates(
        self, authenticated_manager_client, rate_factory, company
    ):
        """
        Given: Manager user
        When: DELETE /rates/:id/
        Then: Returns 403
        """
        rate = rate_factory(company=company)

        response = authenticated_manager_client.delete(f'/api/v1/rates/{rate.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Rate.objects.filter(id=rate.id).exists()


@pytest.mark.django_db
class TestEffectiveRateEndpoint:
    """Tests for GET /api/v1/rates/effective/"""

    def test_get_effective_rate_for_user_project(
        self, authenticated_manager_client, user, project, rate_factory, company
    ):
        """
        Given: Employee-project specific rate exists
        When: GET /rates/effective/?user_id=X&project_id=Y
        Then: Returns that specific rate
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('175.00'),
        )

        response = authenticated_manager_client.get(
            f'/api/v1/rates/effective/?user_id={user.id}&project_id={project.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['rate'] == '175.00'
        assert response.data['source'] == Rate.RateType.EMPLOYEE_PROJECT

    def test_effective_rate_falls_back_to_project(
        self, authenticated_manager_client, user, project, rate_factory, company
    ):
        """
        Given: No employee-project rate, but project rate exists
        When: GET /rates/effective/
        Then: Returns project rate
        """
        rate_factory(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('150.00'),
        )

        response = authenticated_manager_client.get(
            f'/api/v1/rates/effective/?user_id={user.id}&project_id={project.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['rate'] == '150.00'
        assert response.data['source'] == Rate.RateType.PROJECT

    def test_effective_rate_falls_back_to_company(
        self, authenticated_manager_client, user, project, company
    ):
        """
        Given: No specific rates exist
        When: GET /rates/effective/
        Then: Returns company default rate
        """
        response = authenticated_manager_client.get(
            f'/api/v1/rates/effective/?user_id={user.id}&project_id={project.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['source'] == 'COMPANY'

    def test_effective_rate_requires_user_and_project(
        self, authenticated_manager_client
    ):
        """
        Given: Missing parameters
        When: GET /rates/effective/
        Then: Returns 400
        """
        response = authenticated_manager_client.get('/api/v1/rates/effective/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_effective_rate_respects_date(
        self, authenticated_manager_client, user, project, rate_factory, company
    ):
        """
        Given: Rate with specific effective date range
        When: GET /rates/effective/?date=X
        Then: Returns rate effective on that date
        """
        rate_factory(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date.today() - timedelta(days=30),
            effective_to=date.today() - timedelta(days=1),
        )
        rate_factory(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('125.00'),
            effective_from=date.today(),
        )

        response = authenticated_manager_client.get(
            f'/api/v1/rates/effective/?user_id={user.id}&project_id={project.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['rate'] == '125.00'
