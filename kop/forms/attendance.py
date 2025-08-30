from django import forms
from kop.models import TreatmentSession, Patient, PatientTreatment, PatientConsultation
from django.utils import timezone
from dal import autocomplete

from kop.widgets.patient_treatment import PatientTreatmentFormMixin


class CreateAdhocTreatmentSessionForm(forms.ModelForm):
    class Meta:
        model = TreatmentSession
        fields = ['treatment', 'start_time', 'end_time', 'assessment_notes']
        widgets = {
            'treatment': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'assessment_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        self.fields['end_time'].initial = timezone.now().time()
        self.fields['start_time'].initial = (timezone.now() + timezone.timedelta(hours=-1)).time()
        if doctor:
            self.fields['treatment'].queryset = PatientTreatment.objects.filter(doctor=doctor, status="ongoing")
        else:
            self.fields['treatment'].queryset = PatientTreatment.objects.none()



class CreateAdhocConsultationForm(forms.ModelForm):
    class Meta:
        model = PatientConsultation
        fields = ['notes', 'height', 'weight', 'blood_pressure', 'pulse', 'oxygen_saturation', 'chief_complaint',
                  'follow_up_date']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
