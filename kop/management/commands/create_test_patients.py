from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from kop.models import Patient, Branch, LeadSource
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create test patient data'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Number of patients to create')

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']

        # Get or create some branches and lead sources
        branches = list(Branch.objects.all())
        lead_sources = list(LeadSource.objects.all())

        if not branches:
            branches = [Branch.objects.create(name=fake.company(), address=fake.address()) for _ in range(3)]

        if not lead_sources:
            lead_sources = [LeadSource.objects.create(name=source) for source in
                            ['Website', 'Referral', 'Social Media', 'Walk-in']]

        genders = ['M', 'F', 'O']

        for i in range(count):
            # Generate random date of birth (18-80 years old)
            birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

            patient = Patient(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=birth_date,
                gender=random.choice(genders),
                address=fake.address(),
                phone=fake.phone_number()[:20],
                email=fake.unique.email() if i % 3 != 0 else None,  # Some without email
                emergency_contact=fake.name() if i % 4 != 0 else None,
                emergency_phone=fake.phone_number()[:20] if i % 4 != 0 else None,
                medical_history=fake.text() if i % 2 == 0 else None,
                allergies=fake.text() if i % 3 == 0 else None,
                current_medications=fake.text() if i % 4 == 0 else None,
                branch=random.choice(branches) if branches else None,
                is_active=random.choice([True, False]),
                source_of_lead=random.choice(lead_sources) if lead_sources and i % 2 == 0 else None,
            )

            patient.save()

            self.stdout.write(
                self.style.SUCCESS(f'Created patient {i + 1}/{count}: {patient.first_name} {patient.last_name}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} test patients')
        )
