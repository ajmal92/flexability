from datetime import timedelta

from smart_physio.users.models import User
from django.contrib.auth.models import Group, Permission, AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
from slugify import slugify

from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.core.validators import FileExtensionValidator

# User = get_user_model()

from django.db import models
from django.contrib.auth.models import AbstractUser


class AuditModelMixin(models.Model):
    """
    Abstract base model with audit fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from kop.middleware import get_current_user
        user = get_current_user()

        # If creating and created_by is not set
        if not self.pk and not self.created_by:
            self.created_by = user

        # Always update updated_by
        self.updated_by = user

        super().save(*args, **kwargs)


from django.contrib.auth import get_user_model
from django.db.models import Manager


class Branch(AuditModelMixin):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=17)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        branch_admin_group, _ = Group.objects.get_or_create(name=f'branch-admin-{self.name}')
        doctors_branch_group, _ = Group.objects.get_or_create(name=f'doctor-{self.name}')
        staff_branch_group, _ = Group.objects.get_or_create(name=f'staff-{self.name}')
        super().save(*args, **kwargs)


class DoctorSpecialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DoctorProfile(AuditModelMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', unique=True)
    specialization = models.ManyToManyField(DoctorSpecialization, blank=True)
    license_number = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=13)
    years_of_experience = models.PositiveIntegerField(default=0)
    branch = models.ForeignKey(Branch, blank=True, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.name}"

    def get_weekly_availability(self):
        """Returns availability for all days of the week"""
        availability = {}
        for day_code, day_name in WeeklyAvailability.DAY_CHOICES:
            try:
                day_availability = self.weekly_availability.get(day=day_code)
                availability[day_code] = {
                    'is_available': day_availability.is_available,
                    'login_time': day_availability.login_time.strftime(
                        '%H:%M') if day_availability.login_time else None,
                    'logout_time': day_availability.logout_time.strftime(
                        '%H:%M') if day_availability.logout_time else None,
                    'break_start_time': day_availability.break_start_time.strftime(
                        '%H:%M') if day_availability.break_start_time else None,
                    'break_end_time': day_availability.break_end_time.strftime(
                        '%H:%M') if day_availability.break_end_time else None,
                }
            except WeeklyAvailability.DoesNotExist:
                availability[day_code] = {
                    'is_available': False,
                    'login_time': None,
                    'logout_time': None,
                    'break_start_time': None,
                    'break_end_time': None,
                }
        return availability

    def set_default_availability(self):
        """Creates default availability entries for all days"""
        for day_code, day_name in WeeklyAvailability.DAY_CHOICES:
            WeeklyAvailability.objects.get_or_create(
                doctor=self,
                day=day_code,
                defaults={
                    'is_available': day_code not in ['sat', 'sun'],  # Available weekdays by default
                    'login_time': '09:00' if day_code not in ['sat', 'sun'] else None,
                    'logout_time': '17:00' if day_code not in ['sat', 'sun'] else None,
                }
            )

    def save(self, *args, **kwargs):
        doctors_group, _ = Group.objects.get_or_create(name='doctors')
        doctors_branch_group, _ = Group.objects.get_or_create(name=f'doctors-{self.branch}')
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f'{self.user.get_full_name()}'


class WeeklyAvailability(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='weekly_availability', null=True)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    is_available = models.BooleanField(default=True)
    login_time = models.TimeField(null=True, blank=True)
    logout_time = models.TimeField(null=True, blank=True)
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('doctor', 'day')
        ordering = ['day']
        verbose_name_plural = 'Weekly Availabilities'


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

    def save(self, *args, **kwargs):
        # Ensure the user is in the Staff group
        staff_group, _ = Group.objects.get_or_create(name='staff')
        staff_branch_group, _ = Group.objects.get_or_create(name=f'staff-{self.branch}')
        self.user.groups.add(staff_group)
        self.user.groups.add(staff_branch_group)
        super().save(*args, **kwargs)


class LeadSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Lead Source"
        verbose_name_plural = "Lead Sources"
        ordering = ['name']

    def __str__(self):
        return self.name


class Patient(AuditModelMixin):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Basic patient information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True, unique=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)

    # Medical information
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)

    # branch
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='branch', null=True)
    is_active = models.BooleanField(default=True)

    source_of_lead = models.ForeignKey(
        'LeadSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        verbose_name="Source of Lead"
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.phone})'

    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return relativedelta(today, self.date_of_birth).years

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class PatientAttachment(AuditModelMixin):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to='patient_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.patient}"


class TreatmentProgram(AuditModelMixin):
    name = models.CharField(max_length=100)
    rate_per_session = models.DecimalField(max_digits=10, decimal_places=2)
    default_duration = models.PositiveIntegerField(help_text="Duration in days")
    doctors = models.ManyToManyField(DoctorProfile, related_name='treatment_programs')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='treatment_programs')

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


from django.db import models
from django.core.validators import MinValueValidator


class PatientTreatment(models.Model):
    STATUS_CHOICES = [
        ('prescribed', 'Prescribed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='treatments')
    treatment_program = models.ForeignKey('TreatmentProgram', on_delete=models.PROTECT)
    doctor = models.ForeignKey('DoctorProfile', on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    session_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sessions_completed = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Patient Treatment'
        verbose_name_plural = 'Patient Treatments'
        unique_together = ('patient', 'is_active', 'treatment_program')

    def __str__(self):
        return f"{self.patient} - {self.treatment_program}"

    @property
    def pending_sessions(self):
        return self.total_sessions - self.sessions_completed

    @property
    def total_cost(self):
        return self.total_sessions * self.session_rate

    @property
    def amount_paid(self):
        return self.sessions_completed * self.session_rate

    @property
    def balance_due(self):
        return self.pending_sessions * self.session_rate

    @property
    def is_invoice_already_present_for_treatment(self):
        return len(Invoice.objects.filter(patient=self.patient, treatment=self)) > 0

    def save(self, *args, **kwargs):
        from django.contrib import messages

        # First save the treatment to ensure we have an ID
        is_new = self._state.adding  # Check if this is a new instance
        super().save(*args, **kwargs)

        # Create invoice only for new treatments or when status changes to completed
        if not is_new and (self.status not in ['prescribed', 'completed',
                                               'cancelled']) and not self.is_invoice_already_present_for_treatment:
            try:
                # Check if invoice already exists
                if not hasattr(self, 'invoice'):
                    invoice = Invoice.objects.create(
                        patient=self.patient,
                        treatment=self,
                        invoice_date=timezone.now().date(),
                        due_date=timezone.now().date() + timedelta(days=14),
                        status='sent',
                        notes=f"Treatment program: {self.treatment_program.name}",
                        total=self.total_cost,
                        balance=self.total_cost
                    )
                    messages.success(self.request, f"Invoice #{invoice.id} created successfully!")

            except Exception as e:
                # Log the error but don't prevent the treatment from saving
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create invoice for treatment {self.id}: {str(e)}")


class TreatmentSession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    treatment = models.ForeignKey('PatientTreatment', on_delete=models.CASCADE, null=True, blank=True)
    treatment_doctor = models.ForeignKey(
        'DoctorProfile',
        on_delete=models.PROTECT,
        related_name='treatment_sessions'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    assessment_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Treatment Session'
        verbose_name_plural = 'Treatment Sessions'

    def __str__(self):
        return f"{self.treatment} on {self.date}"

    def clean(self):

        from datetime import timedelta

        # Validate session duration (minimum 60 minutes)
        if self.start_time and self.end_time:
            start = timedelta(
                hours=self.start_time.hour,
                minutes=self.start_time.minute
            )
            end = timedelta(
                hours=self.end_time.hour,
                minutes=self.end_time.minute
            )
            if (end - start) < timedelta(minutes=60):
                raise ValidationError("Each session must be at least 60 minutes")

        # Validate that the session date is not in the future when completing
        if self.status == 'completed' and self.date > timezone.now().date():
            raise ValidationError("Cannot complete a session with a future date")

        # Validate that treatment is active if associated with one
        if self.treatment and self.treatment.status != 'ongoing':
            raise ValidationError("Cannot add sessions to a non-ongoing treatment")

    def _handle_session_completion(self):
        """Handle logic when a session is marked as completed"""
        if self.treatment:
            # Check if all sessions are completed
            if self.treatment.sessions_completed >= self.treatment.total_sessions:
                raise ValidationError("All treatment sessions are already completed")

            # Update the treatment's completed sessions count
            self.treatment.sessions_completed = models.F('sessions_completed') + 1

            # If this was the last session, mark treatment as completed
            if self.treatment.sessions_completed + 1 == self.treatment.total_sessions:
                self.treatment.status = 'completed'
                self.treatment.end_date = timezone.now().date()

            self.treatment.save()

    def _handle_session_uncompletion(self):
        """Handle logic when a session is no longer completed"""
        if self.treatment:
            # Ensure we don't go below 0
            if self.treatment.sessions_completed > 0:
                self.treatment.sessions_completed = models.F('sessions_completed') - 1

                # If treatment was completed, revert its status
                if self.treatment.status == 'completed':
                    self.treatment.status = 'ongoing'
                    self.treatment.end_date = None

                self.treatment.save()

    def save(self, *args, **kwargs):
        print('inside save()')
        print(self.pk)
        new_status = self.status
        # Check if this is an existing instance
        if self.pk:
            old_instance = TreatmentSession.objects.get(pk=self.pk)
            old_status = old_instance.status

            # If status changed from non-completed to completed
            if new_status == 'completed' and old_status != 'completed':
                self._handle_session_completion()
            # If status changed from completed to non-completed
            elif old_status == 'completed' and new_status != 'completed':
                self._handle_session_uncompletion()

        if new_status == 'completed':
            self._handle_session_completion()

        super().save(*args, **kwargs)


class PatientWeeklySchedule(AuditModelMixin):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES
    )

    patient_treatment = models.ForeignKey('PatientTreatment', on_delete=models.CASCADE)

    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('patient_treatment', 'day_of_week')
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Patient Weekly Schedule'
        verbose_name_plural = 'Patient Weekly Schedules'

    def __str__(self):
        return f"{self.patient_treatment} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import time, timedelta

        # Validate time slot is at least 30 minutes
        if self.start_time and self.end_time:
            start = timedelta(
                hours=self.start_time.hour,
                minutes=self.start_time.minute
            )
            end = timedelta(
                hours=self.end_time.hour,
                minutes=self.end_time.minute
            )
            if (end - start) < timedelta(minutes=30):
                raise ValidationError("Time slot must be at least 30 minutes")

    @property
    def duration(self):
        """Returns duration in minutes"""
        if self.start_time and self.end_time:
            start = timedelta(
                hours=self.start_time.hour,
                minutes=self.start_time.minute
            )
            end = timedelta(
                hours=self.end_time.hour,
                minutes=self.end_time.minute
            )
            return (end - start).total_seconds() / 60
        return 0

    @property
    def time_slot(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class PatientConsultation(AuditModelMixin):
    CONSULTATION_TYPE_CHOICES = [
        ('initial', 'Initial Consultation'),
        ('followup', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('routine', 'Routine Checkup'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    # Core Fields
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey('DoctorProfile', on_delete=models.PROTECT)
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True)

    # Medical Examination Fields
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in kg
    blood_pressure = models.CharField(max_length=20, blank=True)  # e.g., "120/80"
    pulse = models.PositiveIntegerField(null=True, blank=True)  # BPM
    oxygen_saturation = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]  # SpO2 %
    )
    chief_complaint = models.TextField(blank=True)
    primary_diagnosis = models.TextField(blank=True)
    secondary_diagnosis = models.TextField(blank=True)

    follow_up_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Patient Consultation'
        verbose_name_plural = 'Patient Consultations'

    def __str__(self):
        return f"{self.patient} - {self.date} ({self.consultation_type})"


class Invoice(AuditModelMixin):
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ]
    invoice_number = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    consultation = models.ForeignKey(PatientConsultation, null=True, blank=True, on_delete=models.CASCADE)
    treatment = models.ForeignKey(PatientTreatment, null=True, blank=True, on_delete=models.CASCADE)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'treatment'],
                name='unique_patient_treatment_invoice',
                condition=models.Q(treatment__isnull=False)
            ),
        ]

    # Calculates total automatically
    @property
    def total_cost(self):
        return 600 if self.consultation else self.treatment.total_cost

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number (e.g., INV-2023-001)
            last_invoice = Invoice.objects.order_by('-id').first()
            last_num = int(last_invoice.invoice_number.split('-')[-1]) if last_invoice else 0
            self.invoice_number = f"INV-{timezone.now().year}-{str(last_num + 1).zfill(3)}"

        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)

        super().save(*args, **kwargs)

    @property
    def invoice_type(self):
        return 'Consultation' if self.consultation else 'Treatment'

    @classmethod
    def create_for_consultation(cls, consultation):
        """Helper method to create invoice for a consultation"""
        if consultation.status != 'scheduled':
            raise ValueError("Can only create invoices for scheduled consultations")

        if hasattr(consultation, 'invoice'):
            raise ValueError("Invoice already exists for this consultation")

        return cls.objects.create(
            patient=consultation.patient,
            consultation=consultation,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14),
            status='sent',
            notes=f"Consultation on {consultation.date}",
            balance=600,
            total=600
        )


class BranchAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="branch_admin")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="admins")
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.branch.name})"

    def delete(self, *args, **kwargs):
        """Override delete to also delete the associated User"""
        self.user.delete()  # Delete the associated User first
        super().delete(*args, **kwargs)  # Then delete the BranchAdmin

    @staticmethod
    def generate_default_password(first_name, phone_number):
        return slugify(first_name)[:4] + '@' + phone_number[-4:]

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return f"{self.user.name}"


from django.db.models import Sum


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('insurance', 'Insurance'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True, null=True)

    @property
    def total_payment(self):
        return self.amount + self.discount_amount

    def clean(self):
        """Validate that the payment doesn't exceed the invoice balance"""
        if self.invoice_id:  # Only validate if invoice is set
            # Calculate existing payments (excluding current instance if updating)
            existing_payments = Payment.objects.filter(invoice=self.invoice)
            if self.pk:
                existing_payments = existing_payments.exclude(pk=self.pk)

            existing_total = existing_payments.aggregate(
                total=Sum('amount') + Sum('discount_amount')
            )['total'] or 0

            new_total = existing_total + self.amount + self.discount_amount
            invoice_total = self.invoice.total

            if new_total > invoice_total:
                raise ValidationError(
                    f"Payment amount (${self.total_payment}) exceeds the invoice balance. "
                    f"Maximum allowed: ${invoice_total - existing_total}"
                )

    def save(self, *args, **kwargs):
        # First save the payment
        super().save(*args, **kwargs)

        # Calculate total payments for this invoice
        total_payments = Payment.objects.filter(
            invoice=self.invoice
        ).aggregate(
            total=Sum('amount') + Sum('discount_amount')
        )['total'] or 0

        # Get the invoice total (assuming your Invoice model has a 'total' field)
        # Adjust this based on your actual Invoice model structure
        invoice_total = self.invoice.total  # Replace with your actual invoice total field

        # Mark invoice as paid if total payments >= invoice total
        if total_payments == invoice_total:
            self.invoice.status = 'paid'  # Replace with your actual status field
            self.invoice.balance = 0
            self.invoice.save()
        elif total_payments > invoice_total:
            raise ValidationError(
                f"Payment amount (₹{self.total_payment}) exceeds the invoice balance. "
                f"Maximum allowed: ₹{invoice_total - total_payments}"
            )
        elif total_payments > 0:
            # Optional: Mark as partially paid
            self.invoice.status = 'partially_paid'  # If you have this status
            self.invoice.balance = invoice_total - total_payments  # If you have this status
            self.invoice.save()
