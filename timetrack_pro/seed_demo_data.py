"""
Seed demo data for TimeTrack Pro.
Run with: python manage.py shell < seed_demo_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

from apps.users.models import User
from apps.companies.models import Company, CompanySettings
from apps.projects.models import Project
from apps.rates.models import Rate
from apps.timeentries.models import TimeEntry
from apps.timesheets.models import Timesheet

print("Seeding demo data...")

# Get existing company and admin
company = Company.objects.first()
admin = User.objects.filter(email='admin@timetrack.local').first()

if not company:
    print("No company found. Please create one first.")
    sys.exit(1)

# Create company settings if not exists
CompanySettings.objects.get_or_create(
    company=company,
    defaults={
        'unlock_window_days': 7,
        'daily_warning_threshold': 8,
        'default_hourly_rate': Decimal('75.00'),
    }
)
print(f"Company settings ensured for {company.name}")

# Create demo users
demo_users = [
    {'email': 'john.doe@timetrack.local', 'first_name': 'John', 'last_name': 'Doe', 'role': 'EMPLOYEE'},
    {'email': 'jane.smith@timetrack.local', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'EMPLOYEE'},
    {'email': 'bob.manager@timetrack.local', 'first_name': 'Bob', 'last_name': 'Manager', 'role': 'MANAGER'},
]

created_users = []
for u in demo_users:
    user, created = User.objects.get_or_create(
        email=u['email'],
        defaults={
            'username': u['email'].split('@')[0],
            'first_name': u['first_name'],
            'last_name': u['last_name'],
            'role': u['role'],
            'company': company,
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print(f"Created user: {user.email}")
    created_users.append(user)

john, jane, bob = created_users

# Set manager relationships
john.manager = bob
john.save()
jane.manager = bob
jane.save()
print("Set manager relationships")

# Create projects
projects_data = [
    {'name': 'Website Redesign', 'description': 'Complete website overhaul with new branding'},
    {'name': 'Mobile App Development', 'description': 'iOS and Android app for customer portal'},
    {'name': 'API Integration', 'description': 'Third-party API integrations'},
    {'name': 'Internal Tools', 'description': 'Internal productivity tools and automation'},
    {'name': 'Client Support', 'description': 'Ongoing client support and maintenance'},
]

projects = []
for p in projects_data:
    project, created = Project.objects.get_or_create(
        name=p['name'],
        company=company,
        defaults={'description': p['description'], 'status': 'ACTIVE'}
    )
    if created:
        print(f"Created project: {project.name}")
    projects.append(project)

# Create rates
for project in projects[:3]:
    Rate.objects.get_or_create(
        company=company,
        project=project,
        rate_type='PROJECT',
        defaults={
            'hourly_rate': Decimal('100.00'),
            'effective_from': date.today() - timedelta(days=90),
        }
    )

# Employee rates
for user in [john, jane]:
    Rate.objects.get_or_create(
        company=company,
        employee=user,
        rate_type='EMPLOYEE',
        defaults={
            'hourly_rate': Decimal('85.00'),
            'effective_from': date.today() - timedelta(days=90),
        }
    )
print("Created rates")

# Get current week start (Monday)
today = date.today()
days_since_monday = today.weekday()
week_start = today - timedelta(days=days_since_monday)
last_week_start = week_start - timedelta(days=7)

# Create timesheets
def get_or_create_timesheet(user, week):
    ts, created = Timesheet.objects.get_or_create(
        user=user,
        week_start=week,
        defaults={'status': 'DRAFT'}
    )
    return ts

# Current week timesheets
ts_john = get_or_create_timesheet(john, week_start)
ts_jane = get_or_create_timesheet(jane, week_start)
ts_admin = get_or_create_timesheet(admin, week_start)

# Last week timesheets (submitted/approved)
ts_john_last = get_or_create_timesheet(john, last_week_start)
ts_jane_last = get_or_create_timesheet(jane, last_week_start)

print("Created timesheets")

# Create time entries for current week
def create_entries(user, timesheet, project, week_start, hours_per_day):
    entries = []
    for day_offset in range(5):  # Mon-Fri
        entry_date = week_start + timedelta(days=day_offset)
        entry, created = TimeEntry.objects.get_or_create(
            user=user,
            project=project,
            date=entry_date,
            defaults={
                'timesheet': timesheet,
                'hours': Decimal(str(hours_per_day[day_offset])),
                'description': f'Work on {project.name}',
                'billing_rate': Decimal('100.00'),
                'rate_source': 'PROJECT',
            }
        )
        entries.append(entry)
    return entries

# John's current week entries
create_entries(john, ts_john, projects[0], week_start, [8, 7, 8, 6, 4])
create_entries(john, ts_john, projects[1], week_start, [0, 1, 0, 2, 4])

# Jane's current week entries
create_entries(jane, ts_jane, projects[1], week_start, [6, 8, 7, 8, 6])
create_entries(jane, ts_jane, projects[2], week_start, [2, 0, 1, 0, 2])

# Admin's current week entries
create_entries(admin, ts_admin, projects[3], week_start, [4, 5, 4, 3, 2])
create_entries(admin, ts_admin, projects[4], week_start, [2, 2, 3, 4, 4])

# Last week entries (for approved timesheets)
create_entries(john, ts_john_last, projects[0], last_week_start, [8, 8, 8, 8, 8])
create_entries(jane, ts_jane_last, projects[1], last_week_start, [7, 8, 8, 7, 8])

# Approve last week's timesheets
ts_john_last.status = 'APPROVED'
ts_john_last.submitted_at = timezone.now() - timedelta(days=5)
ts_john_last.approved_at = timezone.now() - timedelta(days=3)
ts_john_last.approved_by = bob
ts_john_last.save()

ts_jane_last.status = 'SUBMITTED'
ts_jane_last.submitted_at = timezone.now() - timedelta(days=2)
ts_jane_last.save()

print("Created time entries")

print("\n=== Demo Data Summary ===")
print(f"Company: {company.name}")
print(f"Users: {User.objects.count()}")
print(f"Projects: {Project.objects.count()}")
print(f"Rates: {Rate.objects.count()}")
print(f"Timesheets: {Timesheet.objects.count()}")
print(f"Time Entries: {TimeEntry.objects.count()}")
print("\nDemo credentials:")
print("  admin@timetrack.local / admin123 (Admin)")
print("  john.doe@timetrack.local / demo123 (Employee)")
print("  jane.smith@timetrack.local / demo123 (Employee)")
print("  bob.manager@timetrack.local / demo123 (Manager)")
print("\nDone!")
