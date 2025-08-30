from dal import autocomplete
from django.urls import reverse
from django import forms


class PatientTreatmentFormMixin(forms.ModelForm):
    class Meta:
        widgets = {
            'treatment': autocomplete.ModelSelect2(
                url='treatment-program-autocomplete',
                attrs={
                    'data-placeholder': 'Search for a treatment...',
                    'data-minimum-input-length': 2,
                    'class': 'form-control select2-autocomplete',
                },
            )
        }
