# utils.py
from django.utils import timezone
from datetime import timedelta, date
from kop.models import PatientTreatment, Patient, Branch, TreatmentSession, PatientConsultation
from django.db import models


def get_expiring_treatments(branch):
    """Get treatments with less than 7 pending sessions"""
    today = timezone.now().date()
    return PatientTreatment.objects.filter(
        patient__branch=branch,
        status='ongoing',
        is_active=True
    ).annotate(
        pending_sessions=models.F('total_sessions') - models.F('sessions_completed')
    ).filter(
        pending_sessions__lt=7
    )


def get_active_patients_count(branch):
    """Get count of active patients in the branch"""
    return Patient.objects.filter(
        branch=branch,
        is_active=True
    ).count()


def get_today_appointments_count(branch):
    """Get count of appointments for today"""
    today = timezone.now().date()
    return PatientConsultation.objects.filter(
        patient__branch=branch,
        date=today
    ).count()


def get_today_treatments_count(branch):
    """Get count of treatments scheduled for today"""
    today = timezone.now().date()
    return TreatmentSession.objects.filter(
        treatment_doctor__branch=branch,
        date=today,
        status='ongoing',
    ).count()


def get_converted_leads_today(branch):
    """Get count of leads converted today"""
    today = timezone.now().date()
    return 0


def get_dashboard_stats(branch):
    """Get all dashboard statistics for a branch"""
    return {
        'expiring_treatments': get_expiring_treatments(branch),
        'expiring_treatments_count': get_expiring_treatments(branch).count(),
        'active_patients_count': get_active_patients_count(branch),
        'today_appointments_count': get_today_appointments_count(branch),
        'today_treatments_count': get_today_treatments_count(branch),
        'converted_leads_today': get_converted_leads_today(branch),
    }
