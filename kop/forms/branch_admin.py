# forms.py
from django import forms
from kop.models import User
from kop.models import BranchAdmin


class BranchAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = BranchAdmin
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'branch']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['first_name'].initial = user.name.split(" ")[0]
            self.fields['last_name'].initial = user.name.split(" ")[1]
            self.fields['email'].initial = user.email
            # self.fields['email'].widget.attrs['disabled'] = True
            # self.fields['last_name'].widget.attrs['disabled'] = True
            # self.fields['first_name'].widget.attrs['disabled'] = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        branch_admin = super().save(commit=False)
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        phone = self.cleaned_data['phone_number']
        if branch_admin.pk:
            user = branch_admin.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = email
            user.save()
        else:
            password = BranchAdmin.generate_default_password(first_name, phone)
            user = User.objects.create_user(
                name = f'{first_name} {last_name}',
                email=email,
                password=password,
                is_staff=True,
            )
            branch_admin.user = user

        if commit:
            branch_admin.save()
        return branch_admin
