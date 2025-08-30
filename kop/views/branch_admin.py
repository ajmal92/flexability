# views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from kop.decorators import superadmin_required
from kop.models import BranchAdmin
from kop.forms.branch_admin import BranchAdminForm
from django.db import models
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from kop.decorators import branch_admin_required
from kop.utils.branch_admin import get_dashboard_stats
from kop.models import Branch


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class BranchAdminListView(ListView):
    model = BranchAdmin
    template_name = "branch_admin/list.html"
    context_object_name = "admins"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related("branch", "user")
        branch = self.request.GET.get("branch")
        search = self.request.GET.get("search")

        if branch:
            qs = qs.filter(branch__id=branch)
        if search:
            qs = qs.filter(
                models.Q(user__first_name__icontains=search)
                | models.Q(phone_number__icontains=search)
            )
        return qs


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class BranchAdminDetailView(DetailView):
    model = BranchAdmin
    template_name = "branch_admin/detail.html"
    context_object_name = "admin"


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class BranchAdminCreateView(CreateView):
    model = BranchAdmin
    form_class = BranchAdminForm
    template_name = "branch_admin/form.html"
    success_url = reverse_lazy("branch_admin_list")


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class BranchAdminUpdateView(UpdateView):
    model = BranchAdmin
    form_class = BranchAdminForm
    template_name = "branch_admin/form.html"
    success_url = reverse_lazy("branch_admin_list")


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class BranchAdminDeleteView(DeleteView):
    model = BranchAdmin
    template_name = "branch_admin/delete.html"
    success_url = reverse_lazy("branch_admin_list")


# views.py

@branch_admin_required
def branch_admin_dashboard(request):
    from django.utils import timezone

    """Dashboard view for branch administrators"""
    # Get the branch associated with the admin
    branch = request.user.branch_admin.branch
    today = timezone.now().date()

    # Get dashboard statistics
    stats = get_dashboard_stats(branch)

    context = {
        'branch': branch,
        'expiring_treatments': stats['expiring_treatments'],
        'expiring_treatments_count': stats['expiring_treatments_count'],
        'active_patients_count': stats['active_patients_count'],
        'today_appointments_count': stats['today_appointments_count'],
        'today_treatments_count': stats['today_treatments_count'],
        'converted_leads_today': stats['converted_leads_today'],
        'today': today
    }

    return render(request, 'branch_admin/dashboard.html', context)
