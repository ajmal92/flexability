from django import forms
from kop.models import PatientConsultation
from django.utils import timezone
import datetime

from kop.widgets.patients import PatientModelFormMixin


class PatientConsultationForm(PatientModelFormMixin):
    class Meta:
        model = PatientConsultation
        fields = '__all__'
        widgets = {
            **PatientModelFormMixin.Meta.widgets,
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d')  # HTML5 date picker restriction
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'value': timezone.now().strftime('%H:%M')
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'value': (timezone.now() + datetime.timedelta(hours=1)).strftime('%H:%M')
            }),
            'follow_up_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d')
            }),
            'chief_complaint': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'primary_diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'secondary_diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'height': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'weight': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'blood_pressure': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'pulse': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'oxygen_saturation': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'doctor': forms.Select({'class': 'form-control'}),
            'status': forms.Select({'class': 'form-control'}),
            'branch': forms.Select({'class': 'form-control'}),
            'consultation_type': forms.Select({'class': 'form-control'})

        }

    def __init__(self, *args, **kwargs):
        # Get initial data from URL or kwargs
        self.patient_id = kwargs.pop('patient_id', None)
        self.consultation_type = kwargs.pop('consultation_type', 'initial')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Set initial values
        if self.patient_id:
            self.fields['patient'].initial = self.patient_id
            self.fields['patient'].disabled = True
            self.fields['patient'].widget.attrs['readonly'] = True
            self.fields['patient'].widget.attrs['style'] = 'pointer-events: none; background-color: #e9ecef;'

        self.fields['consultation_type'].initial = self.consultation_type
        self.fields['status'].initial = 'scheduled'
        self.fields['date'].initial = timezone.now().date()
        # Make patient field read-only if pre-populated
        if self.patient_id and 'patient' in self.fields:
            self.fields['patient'].disabled = True


class PatientConsultationUpdateForm(PatientConsultationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lock certain fields during update
        self.fields['patient'].disabled = True
        self.fields['consultation_type'].disabled = True
        self.fields['date'].disabled = True
