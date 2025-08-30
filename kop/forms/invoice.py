from django import forms
from kop.models import PatientConsultation, PatientTreatment, Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'patient', 'consultation', 'treatment',
            'invoice_date', 'due_date', 'status', 'notes'
        ]
        widgets = {
            'invoice_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Dynamic querysets based on payment type
        self.fields['consultation'].queryset = PatientConsultation.objects.filter(
            patient__branch=user.doctorprofile.branch
        )
        self.fields['treatment'].queryset = PatientTreatment.objects.filter(
            patient__branch=user.doctorprofile.branch
        )

        # JavaScript will handle this, but we'll disable initially
        self.fields['consultation'].widget.attrs['disabled'] = True
        self.fields['treatment'].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')

        # Validate that the correct related field is provided
        if payment_type == 'consultation' and not cleaned_data.get('consultation'):
            self.add_error('consultation', 'Please select a consultation')
        elif payment_type == 'treatment' and not cleaned_data.get('treatment'):
            self.add_error('treatment', 'Please select a treatment')

        return cleaned_data
