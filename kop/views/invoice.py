from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from kop.models import Invoice, Branch

import django_filters


class InvoiceFilter(django_filters.FilterSet):
    patient = django_filters.CharFilter(
        field_name='patient__last_name',
        lookup_expr='icontains',
        label='Patient Last Name'
    )
    branch = django_filters.ModelChoiceFilter(
        field_name='branch',
        queryset=lambda request: request.user.doctorprofile.branch if hasattr(request.user,
                                                                              'doctorprofile') else Branch.objects.none(),
        label='Branch'
    )
    invoice_type = django_filters.ChoiceFilter(
        method='filter_by_type',
        choices=[('consultation', 'Consultation'), ('treatment', 'Treatment')],
        label='Invoice Type'
    )

    class Meta:
        model = Invoice
        fields = []

    def filter_by_type(self, queryset, name, value):
        if value == 'consultation':
            return queryset.filter(consultation__isnull=False)
        elif value == 'treatment':
            return queryset.filter(treatment__isnull=False)
        return queryset


class InvoiceListView(FilterView):
    model = Invoice
    template_name = 'invoices/list.html'
    context_object_name = 'invoices'
    filterset_class = InvoiceFilter
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related(
            'patient',
            'consultation',
            'treatment'
        ).order_by('-invoice_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoices/detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'patient',
            'consultation',
            'treatment',
            'consultation__doctor',
            'treatment__doctor'
        )
