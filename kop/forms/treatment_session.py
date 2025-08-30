from django import forms
from kop.models import TreatmentSession, PatientTreatment, DoctorProfile, Patient
from dal import autocomplete
from django.db import models


class TreatmentSessionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        self.fields['treatment_doctor'].required = False

        # Add form-control class to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # Date and time inputs
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['start_time'].widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
        self.fields['end_time'].widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})

        # Make notes field larger
        self.fields['assessment_notes'].widget.attrs['rows'] = 3

        # Filter treatments by patient if provided
        if patient:
            branch = Patient.objects.get(pk=patient).branch
            doctors = DoctorProfile.objects.filter(branch=branch).all()
            self.fields['treatment'].queryset = PatientTreatment.objects.filter(patient=patient)
            # self.fields['patient'].initial = patient
            self.fields['treatment_doctor'].queryset = doctors

    class Meta:
        model = TreatmentSession
        fields = [
            'treatment',
            'treatment_doctor',
            'date', 'start_time', 'end_time', 'assessment_notes', 'status'
        ]
        widgets = {
            'session_type': forms.Select(attrs={
                'onchange': "toggleConsultationFields(this.value)"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        session_type = cleaned_data.get('session_type')

        # Clear treatment if session is consultation
        if session_type == 'consultation':
            cleaned_data['treatment'] = None

        return cleaned_data


class PatientTreatmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        print('inside get_queryset')
        if not self.request.user.is_authenticated:
            return PatientTreatment.objects.none()

        qs = PatientTreatment.objects.all().select_related('patient', 'doctor')

        # For doctors - only show treatments from their branch
        if hasattr(self.request.user, 'doctor_profile'):
            doctor_branch = self.request.user.doctor_profile.branch
            if doctor_branch:
                qs = qs.filter(doctor__branch=doctor_branch)

        # For staff/superusers - show all treatments
        elif not self.request.user.is_staff and not self.request.user.is_superuser:
            return PatientTreatment.objects.none()

        # Apply search filtering
        if self.q:
            qs = qs.filter(
                models.Q(patient__first_name__icontains=self.q) |
                models.Q(patient__last_name__icontains=self.q) |
                models.Q(patient__phone__icontains=self.q)
            ).distinct()

        print(qs)
        return qs
