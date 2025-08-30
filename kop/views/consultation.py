from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy

from kop.decorators import branch_admin_or_superadmin_required
from kop.models import PatientConsultation, Branch
from kop.forms.consultation import PatientConsultationForm, PatientConsultationUpdateForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
class PatientConsultationCreateView(CreateView):
    model = PatientConsultation
    form_class = PatientConsultationForm
    template_name = 'consultations/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Auto-populate from URL parameters
        kwargs['patient_id'] = self.kwargs.get('patient_id')
        kwargs['consultation_type'] = self.request.GET.get('type', 'initial')
        return kwargs

    def get_success_url(self):
        return reverse_lazy('patient-detail', kwargs={'pk': self.object.patient.id})


@method_decorator(login_required, name='dispatch')
class PatientConsultationUpdateView(UpdateView):
    model = PatientConsultation
    form_class = PatientConsultationUpdateForm
    template_name = 'consultations/form.html'

    def get_success_url(self):
        return reverse_lazy('consultation-detail', kwargs={'pk': self.object.id})

@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
class PatientConsultationDeleteView(DeleteView):
    model = PatientConsultation
    template_name = 'consultations/confirmation_delete.html'

    def get_success_url(self):
        return reverse_lazy('patient-detail', kwargs={'pk': self.object.patient.id})

@method_decorator(login_required, name='dispatch')
class PatientConsultationListView(ListView):
    model = PatientConsultation
    template_name = 'consultations/list.html'
    paginate_by = 10
    ordering = ['-date', '-start_time']
    context_object_name = 'consultations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PatientConsultation.STATUS_CHOICES
        context['branches'] = Branch.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        # Debug print
        queryset = queryset.select_related(
            'patient',
            'doctor__user',
            'patient__branch'
        ).order_by('-date', '-start_time')

        branch = self.request.GET.get('branch')
        patient = self.request.GET.get('patient')
        date = self.request.GET.get('date')
        status = self.request.GET.get('status')

        print(branch, patient, date)

        # Apply filters
        if branch:
            queryset = queryset.filter(
                Q(patient__branch_id=branch) |
                Q(doctor__branch_id=branch)
            )

        # Then filter by patient (if provided)
        if patient:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=patient) |
                Q(patient__last_name__icontains=patient)
            )

        if date:
            queryset = queryset.filter(date=date)

        if status:
            queryset = queryset.filter(status=status)

        return queryset

@method_decorator(login_required, name='dispatch')
class PatientConsultationDetailView(DetailView):
    model = PatientConsultation
    template_name = 'consultations/detail.html'
