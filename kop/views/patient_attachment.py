from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from kop.decorators import branch_admin_or_superadmin_required
from kop.models import Patient, PatientAttachment
from kop.forms.patient_attachment import PatientAttachmentForm

from django.http import FileResponse
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator



@login_required
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(PatientAttachment, pk=attachment_id)

    # if not request.user.has_perm('patients.view_patient', attachment.patient):
    #     raise PermissionDenied()
    response = FileResponse(attachment.file.open(), as_attachment=True)

    # Create a nice filename by combining patient name and attachment title
    filename = f"{slugify(attachment.patient)}-{slugify(attachment.title)}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
@branch_admin_or_superadmin_required
def create_patient_attachment(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = PatientAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.patient = patient
            attachment.save()
            messages.success(request, 'Attachment added successfully!')
            return redirect('patient-detail', pk=patient.id)  # Adjust to your patient detail view
    else:
        form = PatientAttachmentForm()

    context = {
        'form': form,
        'patient': patient,
        'title': 'Add Attachment'
    }
    return render(request, 'patients/attachments/form.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
class PatientAttachmentUpdateView(LoginRequiredMixin, UpdateView):
    model = PatientAttachment
    form_class = PatientAttachmentForm
    template_name = 'patients/attachments/form.html'

    def get_success_url(self):
        messages.success(self.request, 'Attachment updated successfully!')
        return reverse('patient-detail', kwargs={'pk': self.object.patient.id})  # Adjust to your patient detail view

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Attachment'
        context['patient'] = self.object.patient
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(branch_admin_or_superadmin_required, name='dispatch')
class PatientAttachmentDeleteView(LoginRequiredMixin, DeleteView):
    model = PatientAttachment
    template_name = 'patients/attachments/confirmation_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'Attachment deleted successfully!')
        return reverse_lazy('patient-detail', kwargs={'pk': self.object.patient.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context
