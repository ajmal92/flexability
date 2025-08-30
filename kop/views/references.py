from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

from kop.decorators import superadmin_required
from kop.models import LeadSource, DoctorSpecialization, Branch
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required


# LeadSource Views
@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class LeadSourceListView(ListView):
    model = LeadSource
    template_name = 'references/leadsource/list.html'
    context_object_name = 'leadsources'


class LeadSourceCommonFormView:
    model = LeadSource
    template_name = 'references/leadsource/form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('leadsource-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({'class': 'form-control'})
        form.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2  # You can add other attributes too
        })
        # For boolean field (is_active), you might want different styling
        form.fields['is_active'].widget.attrs.update({'class': 'form-check-check'})
        return form


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class LeadSourceCreateView(LeadSourceCommonFormView, CreateView):
    pass


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class LeadSourceUpdateView(LeadSourceCommonFormView, UpdateView):
    pass


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class LeadSourceDetailView(LeadSourceCommonFormView, DetailView):
    model = LeadSource
    template_name = 'references/leadsource/detail.html'
    success_url = None
    fields = None


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class LeadSourceDeleteView(DeleteView):
    model = LeadSource
    template_name = 'references/leadsource/confirmation_delete.html'
    success_url = reverse_lazy('leadsource-list')


class DoctorSpecializationCommonFormView:
    model = DoctorSpecialization
    template_name = 'references/doctor_specialization/form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('doctorspecialization-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({'class': 'form-control'})
        form.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2  # You can add other attributes too
        })
        return form


# DoctorSpecialization Views
class DoctorSpecializationListView(ListView):
    model = DoctorSpecialization
    template_name = 'references/doctor_specialization/list.html'
    context_object_name = 'specializations'


class DoctorSpecializationCreateView(DoctorSpecializationCommonFormView, CreateView):
    pass


class DoctorSpecializationUpdateView(DoctorSpecializationCommonFormView, UpdateView):
    pass


class DoctorSpecializationDetailView(DoctorSpecializationCommonFormView, DetailView):
    model = DoctorSpecialization
    template_name = 'references/doctor_specialization/detail.html'


class DoctorSpecializationDeleteView(DeleteView):
    model = DoctorSpecialization
    template_name = 'references/doctor_specialization/confirmation_delete.html'
    success_url = reverse_lazy('doctorspecialization-list')


# Branch Views
class BranchListView(ListView):
    model = Branch
    template_name = 'references/branch/list.html'
    context_object_name = 'branches'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form


class BranchCommonFormView:
    model = Branch
    template_name = 'references/branch/form.html'
    fields = ['name', 'address', 'phone_number', 'email', 'is_active']
    success_url = reverse_lazy('branch-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({'class': 'form-control'})
        form.fields['phone_number'].widget.attrs.update({'class': 'form-control'})
        form.fields['email'].widget.attrs.update({'class': 'form-control'})
        form.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2  # You can add other attributes too
        })
        # For boolean field (is_active), you might want different styling
        form.fields['is_active'].widget.attrs.update({'class': 'form-check-check'})
        return form


class BranchCreateView(BranchCommonFormView, CreateView):
    pass


class BranchUpdateView(BranchCommonFormView, UpdateView):
    pass


class BranchDetailView(BranchCommonFormView, DetailView):
    model = Branch
    template_name = 'references/branch/detail.html'


class BranchDeleteView(DeleteView):
    model = Branch
    template_name = 'references/branch/confirmation_delete.html'
    success_url = reverse_lazy('branch-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form
