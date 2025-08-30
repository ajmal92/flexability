from django.views.generic import (
    CreateView, UpdateView, DeleteView,
    ListView, DetailView
)
from django.urls import reverse_lazy
from django.db.models import Q
from kop.models import TreatmentSession, PatientTreatment, Branch
from kop.forms.treatment_session import TreatmentSessionForm
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class TreatmentSessionCreateView(CreateView):
    model = TreatmentSession
    form_class = TreatmentSessionForm
    template_name = 'treatment_sessions/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        print(kwargs, self.kwargs)
        if 'patient_id' in self.kwargs:
            kwargs['patient'] = self.kwargs['patient_id']
        return kwargs

    def get_success_url(self):
        return reverse_lazy('treatment-session-detail', kwargs={'pk': self.object.pk})


class SessionUpdateView(UpdateView):
    model = TreatmentSession
    form_class = TreatmentSessionForm
    template_name = 'treatment_sessions/form.html'

    def get_success_url(self):
        return reverse_lazy('session-detail', kwargs={'pk': self.object.pk})


class SessionDetailView(DetailView):
    model = TreatmentSession
    template_name = 'treatment_sessions/detail.html'
    context_object_name = 'session'


class TreatmentSessionDeleteView(DeleteView):
    model = TreatmentSession
    template_name = 'treatment_sessions/confirm_delete.html'
    success_url = reverse_lazy('treatment-session-list')


class TreatmentSessionListView(ListView):
    model = TreatmentSession
    template_name = 'treatment_sessions/list.html'
    paginate_by = 10
    context_object_name = 'treatment_sessions'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'treatment', 'treatment_doctor__user'
        )

        # Get filter parameters
        branch = self.request.GET.get('branch')
        patient = self.request.GET.get('patient')
        date = self.request.GET.get('date')
        treatment = self.request.GET.get('treatment')  # New treatment filter

        # Apply filters
        if branch:
            queryset = queryset.filter(
                Q(treatment__treatment_program__branch_id=branch) |
                Q(treatment_doctor__branch_id=branch)
            )

        # Filter by treatment first (if provided)
        if treatment:
            queryset = queryset.filter(treatment_id=treatment)

        # Then filter by patient (if provided)
        if patient:
            queryset = queryset.filter(
                Q(treatment__patient__first_name__icontains=patient) |
                Q(treatment__patient__last_name__icontains=patient)
            )

        if date:
            queryset = queryset.filter(date=date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add treatments to context for filter dropdown
        context['branches'] = Branch.objects.all()

        context['treatments'] = PatientTreatment.objects.filter(
            status='ongoing'
        ).select_related('patient', 'treatment_program')

        # Preserve filter parameters in context
        context['current_branch'] = self.request.GET.get('branch', '')
        context['current_patient'] = self.request.GET.get('patient', '')
        context['current_date'] = self.request.GET.get('date', '')
        context['current_treatment'] = self.request.GET.get('treatment', '')

        return context
