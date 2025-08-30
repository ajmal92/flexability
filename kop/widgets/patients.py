from dal import autocomplete
from django.urls import reverse
from django import forms

class PatientModelFormMixin(forms.ModelForm):
    """
    Base form mixin that includes the standardized patient dropdown
    """

    class Meta:
        widgets = {
            'patient': autocomplete.ModelSelect2(
                url='patient-autocomplete',
                attrs={
                    # 'data-placeholder': 'Search for a patient...',
                    'data-minimum-input-length': 2,
                    'class': 'form-control select2-autocomplete',
                },
            )
        }
