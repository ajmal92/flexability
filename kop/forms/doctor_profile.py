from django import forms
from kop.models import DoctorProfile, User, DoctorSpecialization, Branch
from slugify import slugify


class DoctorForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    specialization = forms.ModelMultipleChoiceField(
        queryset=DoctorSpecialization.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    class Meta:
        model = DoctorProfile
        fields = ['license_number', 'years_of_experience', 'address', 'branch', 'specialization', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['name'].initial = self.instance.user.name

    def save(self, commit=True):
        # Get or create user
        email = self.cleaned_data['email']
        name = self.cleaned_data['name']
        phone_number = self.cleaned_data['phone_number']

        if self.instance.pk:
            # Update existing
            user = self.instance.user
            user.email = email
            user.name = name
            user.save()
        else:
            # Create new
            user = User.objects.create_user(
                email=email,
                name=name,
                is_staff=True,
                password=slugify(name)[:4] + '@' + phone_number[-4:]
            )

        doctor = super().save(commit=False)
        doctor.user = user

        if commit:
            doctor.save()
            self.save_m2m()  # For many-to-many fields like specialization

        return doctor
