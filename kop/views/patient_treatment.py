from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from kop.models import PatientTreatment, Branch, DoctorProfile
from kop.forms.patient_treament import PatientTreatmentForm


class PatientTreatmentListView(ListView):
    model = PatientTreatment
    template_name = 'patient_treatment/list.html'
    context_object_name = 'page_obj'  # Changed to work with pagination
    paginate_by = 10  # 10 results per page

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'patient', 'treatment_program', 'doctor__user', 'treatment_program__branch'
        )

        # Get filter parameters
        patient = self.request.GET.get('patient')
        doctor = self.request.GET.get('doctor')
        status = self.request.GET.get('status')
        branch = self.request.GET.get('branch')

        # Apply filters
        if patient:
            queryset = queryset.filter(patient__first_name__icontains=patient)
        if doctor:
            queryset = queryset.filter(doctor__user__name__icontains=doctor)
        if status:
            queryset = queryset.filter(status=status)
        if branch:
            queryset = queryset.filter(treatment_program__branch_id=branch)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PatientTreatment.STATUS_CHOICES
        context['branches'] = Branch.objects.all()
        # Pass current filter values back to template
        context['current_patient'] = self.request.GET.get('patient', '')
        context['current_doctor'] = self.request.GET.get('doctor', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_branch'] = self.request.GET.get('branch', '')
        return context


class PatientTreatmentCreateView(CreateView):
    model = PatientTreatment
    form_class = PatientTreatmentForm
    template_name = 'patient_treatment/form.html'
    success_url = reverse_lazy('patient-treatment-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'patient': self.kwargs.get('patient_id')}  # Ensure rate is empty by default
        kwargs['user'] = self.request.user

        return kwargs

    def form_invalid(self, form):
        print("Form errors:", form.errors)  # Debug output
        return super().form_invalid(form)


class PatientTreatmentUpdateView(UpdateView):
    model = PatientTreatment
    form_class = PatientTreatmentForm
    template_name = 'patient_treatment/form.html'
    success_url = reverse_lazy('patient-treatment-list')


class PatientTreatmentDetailView(DetailView):
    model = PatientTreatment
    template_name = 'patient_treatment/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['treatment_sessions'] = TreatmentSession.objects.filter(
        #     treatment=self.object
        # ).order_by('-date')[:5]  # Last 5 treatment_sessions
        context['treatment_sessions'] = []
        return context


from kop.models import PatientTreatment, Patient
