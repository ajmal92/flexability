from django import forms
from kop.models import PatientAttachment


class PatientAttachmentForm(forms.ModelForm):
    class Meta:
        model = PatientAttachment
        fields = ['file', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': '.pdf'})
        self.fields['title'].widget.attrs.update({'placeholder': 'Enter attachment title'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})
