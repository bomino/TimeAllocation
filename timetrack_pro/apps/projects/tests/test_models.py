"""
Tests for Project models - TDD approach.
"""
import pytest
from django.db import IntegrityError

from apps.projects.models import Project


@pytest.mark.django_db
class TestProjectModel:
    """Tests for Project model."""

    def test_create_project_with_required_fields(self, company):
        """
        Given: A company
        When: Creating a project with name and company
        Then: Project is created successfully
        """
        project = Project.objects.create(
            name='Test Project',
            company=company,
        )

        assert project.pk is not None
        assert project.name == 'Test Project'
        assert project.company == company
        assert project.status == Project.Status.ACTIVE

    def test_project_default_status_is_active(self, company):
        """
        Given: Creating a new project
        When: No status is specified
        Then: Status defaults to ACTIVE
        """
        project = Project.objects.create(
            name='New Project',
            company=company,
        )

        assert project.status == Project.Status.ACTIVE

    def test_project_name_unique_per_company(self, company):
        """
        Given: A project with name 'Project A' in company X
        When: Creating another project with same name in same company
        Then: IntegrityError is raised
        """
        Project.objects.create(name='Project A', company=company)

        with pytest.raises(IntegrityError):
            Project.objects.create(name='Project A', company=company)

    def test_same_project_name_allowed_in_different_companies(self, company, company_factory):
        """
        Given: A project with name 'Project A' in company X
        When: Creating project with same name in company Y
        Then: Both projects are created successfully
        """
        other_company = company_factory(name='Other Company')

        project1 = Project.objects.create(name='Shared Name', company=company)
        project2 = Project.objects.create(name='Shared Name', company=other_company)

        assert project1.pk != project2.pk
        assert project1.name == project2.name

    def test_project_str_returns_name(self, company):
        """
        Given: A project with name 'My Project'
        When: Converting to string
        Then: Returns the project name
        """
        project = Project.objects.create(name='My Project', company=company)

        assert str(project) == 'My Project'

    def test_project_has_timestamps(self, company):
        """
        Given: A newly created project
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        project = Project.objects.create(name='Timestamped', company=company)

        assert project.created_at is not None
        assert project.updated_at is not None

    def test_project_status_choices(self):
        """
        Given: Project status choices
        When: Checking available options
        Then: ACTIVE, INACTIVE, ARCHIVED are available
        """
        assert Project.Status.ACTIVE == 'ACTIVE'
        assert Project.Status.INACTIVE == 'INACTIVE'
        assert Project.Status.ARCHIVED == 'ARCHIVED'

    def test_project_can_have_description(self, company):
        """
        Given: Creating a project
        When: Providing a description
        Then: Description is saved
        """
        project = Project.objects.create(
            name='Described Project',
            company=company,
            description='This is a detailed project description.',
        )

        assert project.description == 'This is a detailed project description.'

    def test_project_description_defaults_to_empty(self, company):
        """
        Given: Creating a project
        When: No description provided
        Then: Description is empty string
        """
        project = Project.objects.create(name='No Desc', company=company)

        assert project.description == ''


@pytest.mark.django_db
class TestProjectRelationships:
    """Tests for Project model relationships."""

    def test_company_can_have_multiple_projects(self, company):
        """
        Given: A company
        When: Creating multiple projects for it
        Then: All projects are accessible via company.projects
        """
        Project.objects.create(name='Project 1', company=company)
        Project.objects.create(name='Project 2', company=company)
        Project.objects.create(name='Project 3', company=company)

        assert company.projects.count() == 3

    def test_deleting_company_cascades_to_projects(self, company):
        """
        Given: A company with projects
        When: Company is deleted
        Then: All its projects are deleted
        """
        Project.objects.create(name='Project A', company=company)
        Project.objects.create(name='Project B', company=company)
        company_id = company.id

        company.delete()

        assert Project.objects.filter(company_id=company_id).count() == 0
