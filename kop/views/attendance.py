from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse

from kop.decorators import doctor_required
from kop.models import TreatmentSession, DoctorProfile, TreatmentProgram, Patient, PatientConsultation
from kop.forms.attendance import CreateAdhocTreatmentSessionForm
from django.utils import timezone
from django.urls import reverse

from .. import models


@doctor_required
def doctor_dashboard(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Session Statistics
    total_sessions = TreatmentSession.objects.filter(treatment_doctor=doctor).count()
    monthly_sessions = TreatmentSession.objects.filter(
        treatment_doctor=doctor,
        date__month=current_month,
        date__year=current_year,
        status='completed'
    ).count()
    todays_completed = TreatmentSession.objects.filter(
        treatment_doctor=doctor,
        date=today,
        status='completed'
    ).count()

    # Consultation Statistics
    total_consultations = PatientConsultation.objects.filter(doctor=doctor).count()
    monthly_consultations = PatientConsultation.objects.filter(
        doctor=doctor,
        date__month=current_month,
        date__year=current_year,
        status='completed'
    ).count()
    todays_completed_consultations = PatientConsultation.objects.filter(
        doctor=doctor,
        date=today,
        status='completed'
    ).count()

    # Patient Statistics
    assigned_patients = Patient.objects.filter(
        treatments__doctor=doctor
    ).distinct().count()

    context = {
        'stats': {
            # Treatment Sessions
            'total_sessions': total_sessions,
            'monthly_sessions': monthly_sessions,
            'todays_completed': todays_completed,
            'scheduled_today': TreatmentSession.objects.filter(
                treatment_doctor=doctor,
                date=today,
                status='scheduled'
            ).count(),

            # Consultations
            'total_consultations': total_consultations,
            'monthly_consultations': monthly_consultations,
            'todays_completed_consultations': todays_completed_consultations,
            'scheduled_consultations_today': PatientConsultation.objects.filter(
                doctor=doctor,
                date=today,
                status='scheduled'
            ).count(),

            # Patients
            'assigned_patients': assigned_patients,
        },
        'todays_sessions': TreatmentSession.objects.filter(
            treatment_doctor=doctor,
            date=today
        ).order_by('start_time'),
        'today': today,
        'todays_consultations': PatientConsultation.objects.filter(
            doctor=doctor,
            date=today
        ).order_by('start_time'),
    }
    return render(request, 'doctors/dashboard.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from kop.forms.attendance import CreateAdhocConsultationForm


@require_POST
def complete_consultation(request, pk):
    try:
        consultation = PatientConsultation.objects.get(pk=pk)
        form = CreateAdhocConsultationForm(request.POST, instance=consultation)

        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.status = 'completed'
            consultation.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid form data'})

    except PatientConsultation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Consultation not found'}, status=404)


@doctor_required
def mark_attendance(request, session_id=None):
    doctor = DoctorProfile.objects.get(user=request.user)
    today = timezone.now().date()
    session = None
    form = CreateAdhocTreatmentSessionForm(request.POST or None, doctor=doctor)

    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        if not session_id:  # Only set these for new sessions
            session.treatment_doctor = doctor
            session.date = today
            session.status = 'completed'
        session.save()
        messages.success(request, 'Session recorded successfully!')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect': reverse('doctor_dashboard')})
        else:
            return redirect('doctor_dashboard')

    return render(request, 'doctors/mark_attendance.html', {
        'form': form,
        'session': session,
        'is_new': session_id is None,
        'today': today
    })


from dal import autocomplete
from kop.models import Patient
from django.db import models
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class PatientAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Patient.objects.all()
        if hasattr(self.request.user, 'doctor_profile'):
            qs = qs.filter(branch=self.request.user.doctor_profile.branch)

        if self.q:
            qs = qs.filter(
                models.Q(first_name__icontains=self.q) |
                models.Q(phone__icontains=self.q)
            )
        return qs
