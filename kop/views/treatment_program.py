from rest_framework import viewsets, filters

from kop.decorators import branch_admin_or_superadmin_required, superadmin_required
from kop.forms.treatment_program import TreatmentProgramForm
from kop.models import TreatmentProgram, Branch
from kop.serializers.treatment_program import TreatmentProgramSerializer, TreatmentProgramListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class TreatmentProgramViewSet(viewsets.ModelViewSet):
    queryset = TreatmentProgram.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch']
    search_fields = ['name']
    ordering_fields = ['name', 'rate_per_session', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TreatmentProgramListSerializer
        return TreatmentProgramSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('doctor_id'):
            queryset = queryset.filter(doctors__id=self.request.query_params.get('doctor_id'))
        return queryset.select_related('branch').prefetch_related('doctors')


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class TreatmentProgramListView(ListView):
    model = TreatmentProgram
    template_name = 'treatment_programs/list.html'
    context_object_name = 'treatment_programs'
    paginate_by = 10  # 10 items per page

    def get_queryset(self):
        queryset = super().get_queryset().select_related('branch').prefetch_related('doctors')

        # Get filter parameters
        search_query = self.request.GET.get('search')
        branch_id = self.request.GET.get('branch')

        # Apply filters
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add branches to context for filter dropdown
        context['branches'] = Branch.objects.all()
        # Pass current filter values back to template
        context['current_search'] = self.request.GET.get('search', '')
        context['current_branch'] = self.request.GET.get('branch', '')
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class TreatmentProgramCreateView(CreateView):
    model = TreatmentProgram
    form_class = TreatmentProgramForm
    template_name = 'treatment_programs/form.html'
    success_url = reverse_lazy('treatment-program-list')


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class TreatmentProgramUpdateView(UpdateView):
    model = TreatmentProgram
    form_class = TreatmentProgramForm
    template_name = 'treatment_programs/form.html'
    success_url = reverse_lazy('treatment-program-list')


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class TreatmentProgramDeleteView(DeleteView):
    model = TreatmentProgram
    template_name = 'treatment_programs/confirm_delete.html'
    success_url = reverse_lazy('treatment-program-list')
