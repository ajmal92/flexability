from kop import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

from kop.models import TreatmentSession, PatientConsultation, Invoice


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
