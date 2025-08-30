from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from kop.models import PatientWeeklySchedule
from kop.forms.patient_weekly_schedule import PatientWeeklyScheduleForm


class PatientWeeklyScheduleCreateView(CreateView):
    model = PatientWeeklySchedule
    form_class = PatientWeeklyScheduleForm
    template_name = 'patients/schedules/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'patient_id' in self.kwargs:
            kwargs['initial'] = {'patient': self.kwargs['patient_id']}
        return kwargs

    def get_success_url(self):
        return reverse_lazy('patient-weekly-schedule-list', kwargs={'patient_id': self.object.patient_treatment.patient.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient_id'] = self.kwargs.get('patient_id')
        return context


class PatientWeeklyScheduleUpdateView(UpdateView):
    model = PatientWeeklySchedule
    form_class = PatientWeeklyScheduleForm
    template_name = 'patients/schedules/form.html'

    def get_success_url(self):
        return reverse_lazy('patient-weekly-schedule-list', kwargs={'patient_id': self.object.patient.id})


class PatientWeeklyScheduleListView(ListView):
    model = PatientWeeklySchedule
    template_name = 'patients/schedules/list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        qs_all = super().get_queryset()
        patient_id = self.kwargs['patient_id']
        qs = qs_all.filter(patient_treatment__patient_id=patient_id)
        print(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.get_queryset().first().patient_treatment.patient if self.get_queryset().exists() else None
        print(context)
        return context


class PatientWeeklyScheduleDeleteView(DeleteView):
    model = PatientWeeklySchedule
    template_name = 'patients/schedules/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('patient-weekly-schedule-list', kwargs={'patient_id': self.object.patient.id})
