from django import forms
from kop.models import PatientWeeklySchedule, PatientTreatment


class PatientWeeklyScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        print('#####', kwargs)
        patient_id = kwargs['initial']['patient']
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        # Special field handling
        print('########', patient_id)
        if patient_id:
            treatments = PatientTreatment.objects.filter(patient_id=patient_id)

            if treatments.count() == 1:
                # Auto-select the only treatment and hide the field
                self.fields['patient_treatment'].initial = treatments.first()
                self.fields['patient_treatment'].widget = forms.HiddenInput()
            else:
                # Show dropdown with filtered treatments
                self.fields['patient_treatment'].queryset = treatments
                self.fields['patient_treatment'].widget.attrs['class'] = 'form-select'


        self.fields['start_time'].widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
        self.fields['end_time'].widget = forms.TimeInput(attrs={'type': 'time','class': 'form-control'})
        self.fields['notes'].widget.attrs['rows'] = 3
        self.fields['day_of_week'].widget.attrs['class'] = 'form-select'
        # self.fields['is_active'].widget = forms.BooleanField()

    class Meta:
        model = PatientWeeklySchedule
        fields = '__all__'
        widgets = {
            'created_by': forms.HiddenInput(),
            'updated_by': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Additional validation can be added here
        return cleaned_data
