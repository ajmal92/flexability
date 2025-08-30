from django import forms
from kop.models import Patient, PatientAttachment, Branch
from django.core.validators import FileExtensionValidator


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'address', 'phone', 'email', 'emergency_contact',
            'emergency_phone', 'medical_history', 'allergies',
            'current_medications', 'branch', 'is_active', 'source_of_lead'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if field_name != 'is_active':  # Handle checkbox separately
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

        # Specific widget adjustments
        self.fields['date_of_birth'].widget.attrs['type'] = 'date'
        self.fields['is_active'].label = 'Active'

        if self.user and hasattr(self.user, 'branch_admin'):
            branch = self.user.branch_admin.branch
            self.fields['branch'].initial = branch
            # For existing instances, don't change the branch field behavior
            if not self.instance.pk:
                self.fields['branch'].widget.attrs['readonly'] = True
                self.fields['branch'].widget.attrs['disabled'] = True

            # For superadmins, show all branches
        elif self.user and self.user.is_superuser:
            self.fields['branch'].queryset = Branch.objects.all()
        else:
            # For other users, limit to their branch if applicable
            self.fields['branch'].queryset = Branch.objects.none()


class PatientSearchForm(forms.Form):
    name = forms.CharField(required=False, label='Name', widget=forms.TextInput(attrs={
        'placeholder': 'Search by name',
        'class': 'form-control'
    }))
    phone = forms.CharField(required=False, label='Phone', widget=forms.TextInput(attrs={
        'placeholder': 'Search by phone',
        'class': 'form-control'
    }))
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        label='Branch',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Get user from kwargs if passed
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Limit branch choices for branch admins
        if self.user and hasattr(self.user, 'branch_admin'):
            self.fields['branch'].queryset = Branch.objects.filter(id=self.user.branch_admin.branch.id)
            self.fields['branch'].initial = self.user.branch_admin.branch
            self.fields['branch'].empty_label = None  # Remove empty choice


class PatientAttachmentForm(forms.ModelForm):
    class Meta:
        model = PatientAttachment
        fields = ['file', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
        return file
