from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from kop.decorators import superadmin_required, doctor_or_superadmin_required, branch_admin_or_superadmin_required
from kop.forms.patient import PatientForm, PatientSearchForm
from kop.models import *
from kop.serializers.patients import PatientSerializer
from kop.utils.common import get_user_branch
from kop.views.doctorprofile import SerializerBase
from django.contrib import messages


class PatientViewSet(SerializerBase):
    serializer_class = PatientSerializer

    queryset = Patient.objects.all()

    filterset_fields = {
        'branch': ['exact'],
        'is_active': ['exact'],
        'is_active': ['exact'],
    }

    # Fields to search in (partial matches)
    search_fields = ['first_name']

    # Fields available for ordering
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']  # Default ordering


@login_required
def patient_list(request):
    doctor_or_admin = hasattr(request.user, 'doctor_profile') or hasattr(request.user, 'branch_admin')
    if request.user and doctor_or_admin:
        branch = get_user_branch(request.user)
        patients = Patient.objects.filter(branch=branch).order_by('-created_at')
    else:
        patients = Patient.objects.all().order_by('-created_at')

    # Search functionality
    search_form = PatientSearchForm(request.GET or None, user=request.user)
    if search_form.is_valid():
        name = search_form.cleaned_data['name']
        phone = search_form.cleaned_data['phone']
        branch = search_form.cleaned_data['branch']
        filters = Q()

        if name:
            filters &= (Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if phone:
            filters &= Q(phone__icontains=phone)

        if branch:
            filters &= Q(branch=branch)

        patients = patients.filter(filters)

    else:
        print("Form errors:", search_form.errors)

    # Pagination
    paginator = Paginator(patients, 10)  # Show 20 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'patients/list.html', context)


@login_required
@branch_admin_or_superadmin_required
def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, user=request.user)
        if form.is_valid():
            patient = form.save()
            return redirect('patient-detail', pk=patient.id)
    else:
        form = PatientForm(user=request.user)

    context = {'form': form}
    return render(request, 'patients/form.html', context)


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    attachments = PatientAttachment.objects.filter(patient=patient)
    invoices = Invoice.objects.filter(patient=patient).order_by('-invoice_date')
    payments = Payment.objects.filter(invoice__patient=patient).select_related('invoice').order_by('-payment_date')

    if request.method == 'POST':
        return redirect('patients/detail', patient_id=patient.id)

    return render(request, 'patients/detail.html', {
        'patient': patient,
        'attachments': attachments,
        'invoices': invoices,
        'payments': payments,  # Add payments to context
    })


@login_required
@branch_admin_or_superadmin_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient-detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)

    context = {'form': form, 'patient': patient}
    return render(request, 'patients/form.html', context)


@login_required
@branch_admin_or_superadmin_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.delete()
        return redirect('patient-list')

    context = {'patient': patient}
    return render(request, 'patients/confirm_delete.html', context)
