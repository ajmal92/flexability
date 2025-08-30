from django import forms
from kop.models import TreatmentProgram, DoctorProfile


class TreatmentProgramForm(forms.ModelForm):
    class Meta:
        model = TreatmentProgram
        fields = ['name', 'rate_per_session', 'default_duration', 'branch', 'doctors']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rate_per_session': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01
            }),
            'default_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'doctors': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['doctors'].queryset = self.instance.branch.doctorprofile_set.all()
        elif 'branch' in self.data:
            branch_id = self.data.get('branch')
            self.fields['doctors'].queryset = DoctorProfile.objects.filter(branch_id=branch_id)
