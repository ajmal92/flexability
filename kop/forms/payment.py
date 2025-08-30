# forms.py
from django import forms
from kop.models import Payment, Invoice


class PaymentForm(forms.ModelForm):
    discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    class Meta:
        model = Payment
        fields = ['amount', 'discount_amount', 'method', 'reference', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this payment...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)

        if self.invoice:
            self.fields['amount'].widget.attrs['max'] = float(self.invoice.total_cost)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount', 0)
        discount_amount = cleaned_data.get('discount_amount', 0) or 0
        total_payment = amount + discount_amount

        if self.invoice and total_payment > self.invoice.total_cost:
            raise forms.ValidationError(
                f"Total payment (amount + discount) cannot exceed amount due: ${self.invoice.total_cost}"
            )

        return cleaned_data
