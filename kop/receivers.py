from kop import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

from kop.models import TreatmentSession, PatientConsultation, Invoice


@receiver(post_save, sender=PatientConsultation)
def create_consultation_invoice(sender,instance, **kwargs):
    """
    Automatically creates invoice when consultation is marked as completed
    """
    print('inside post_save-create_consultation_invoice')
    if instance.status == 'completed':
        # Check if status was changed to completed
        try:
            old_instance = PatientConsultation.objects.get(pk=instance.pk)
            if old_instance.status != 'completed':
                try:
                    Invoice.create_for_consultation(instance)
                    # You might want to add logging here
                except ValueError as e:
                    # Log error if invoice creation fails
                    from django.core.exceptions import ValidationError
                    raise ValidationError(f"Invoice creation failed: {str(e)}")
        except PatientConsultation.DoesNotExist:
            pass


@receiver(pre_delete, sender=TreatmentSession)
def handle_session_deletion(sender, instance, **kwargs):
    """Handle logic when a session is deleted"""
    if instance.status == 'completed' and instance.treatment:
        # Ensure we don't go below 0
        if instance.treatment.sessions_completed > 0:
            instance.treatment.sessions_completed = models.F('sessions_completed') - 1

            # If treatment was completed, check if we need to revert its status
            if (instance.treatment.status == 'completed' and
                instance.treatment.sessions_completed < instance.treatment.total_sessions):
                instance.treatment.status = 'ongoing'
                instance.treatment.end_date = None

            instance.treatment.save()
