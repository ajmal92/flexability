from django import forms

from kop.forms.consultation import PatientModelFormMixin
from kop.models import PatientTreatment, DoctorProfile, Patient


class PatientTreatmentForm(PatientModelFormMixin):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)
        patient_id = self.initial.get('patient')
        if patient_id:
            try:
                patient = Patient.objects.get(pk=patient_id)
                self.fields['patient'].initial = patient
                # self.fields['patient'].disabled = True
                self.fields['patient'].queryset = Patient.objects.filter(pk=patient_id)
                self.fields['patient'].widget.attrs.update({
                    'readonly': 'readonly',
                    'class': 'form-control'
                })
            except Patient.DoesNotExist:
                pass
        if user and hasattr(user, 'doctor_profile'):
            # Set initial value to the logged-in doctor's profile
            self.fields['doctor'].initial = user.doctor_profile
            # Make the field disabled
            self.fields['doctor'].disabled = True
            # Limit queryset to only this doctor
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(user=user)

            # You might also want to add a widget attribute to make it clear it's read-only
            self.fields['doctor'].widget.attrs.update({
                'readonly': 'readonly',
                'class': 'form-control'
            })

            self.fields['status'].initial = 'assigned'
            self.fields['session_rate'].required = False

    class Meta:
        model = PatientTreatment
        fields = [
            'patient', 'treatment_program', 'doctor',
            'total_sessions', 'session_rate',
            'end_date', 'status', 'notes'
        ]
        widgets = {
            **PatientModelFormMixin.Meta.widgets,
            'status': forms.Select(choices=PatientTreatment.STATUS_CHOICES, attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3,'class': 'form-control'}),
            'session_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_sessions': forms.NumberInput(attrs={'class': 'form-control'}),
            'treatment_program': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        treatment_program = cleaned_data.get('treatment_program')
        session_rate = cleaned_data.get('session_rate')

        # Set default session rate if not provided
        if treatment_program and not session_rate:
            cleaned_data['session_rate'] = treatment_program.rate_per_session

        return cleaned_data
