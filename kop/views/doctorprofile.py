from rest_framework import  status
from rest_framework.permissions import IsAuthenticated

from kop.decorators import doctor_required, superadmin_required
from kop.forms.doctor_profile import DoctorForm
from kop.permissions.doctorprofile import DoctorViewPermission, DoctorModifyPermission
from kop.serializers.doctorprofile import WeeklyAvailabilitySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.utils.decorators import method_decorator

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from kop.models import *

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from kop.models import WeeklyAvailability, DoctorProfile
from django.db.models import Case, When

from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from kop.widgets.login import LoginRequiredMixIn


class SerializerBase(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Add filter backends
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), DoctorModifyPermission()]
        return [IsAuthenticated(), DoctorViewPermission()]

    def _is_superadmin_or_branchadmin(self, user, doctor):
        """Helper method to check if user can modify a doctor"""
        if user.is_superuser:
            return True
        if hasattr(user, 'branch_admin_profile'):
            return doctor.branch == user.branch_admin_profile.branch
        return False

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['updated_by'] = request.user

        # Check if user has permission to update this doctor
        if not self._is_superadmin_or_branchadmin(request.user, instance):
            return Response(
                {"detail": "You do not have permission to modify this doctor."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if user has permission to delete this doctor
        if not self._is_superadmin_or_branchadmin(request.user, instance):
            return Response(
                {"detail": "You do not have permission to delete this doctor."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    def get_create_permissions(self, request):
        return request.user.is_superuser or hasattr(request.user, 'branch_admin_profile')

    def create(self, request, *args, **kwargs):
        # Only allow creation if user is superadmin or branch admin
        if not (request.user.is_superuser or hasattr(request.user, 'branch_admin_profile')):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # For branch admins, automatically assign their branch
        if hasattr(request.user, 'branch_admin_profile'):
            serializer.validated_data['branch'] = request.user.branch_admin_profile.branch

        serializer.validated_data['created_by'] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


from django.views.generic import DetailView


class DoctorDetailView(LoginRequiredMixIn, DetailView):
    model = DoctorProfile
    template_name = 'doctors/detail.html'

    # context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context you need
        print(context['object'].specialization)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(superadmin_required, name='dispatch')
class DoctorCreateView(CreateView):
    model = DoctorProfile
    form_class = DoctorForm
    template_name = 'doctors/form.html'
    success_url = reverse_lazy('doctor-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['specializations'] = DoctorSpecialization.objects.all()
        return context


@method_decorator(doctor_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DoctorUpdateView(UpdateView):
    model = DoctorProfile
    form_class = DoctorForm
    template_name = 'doctors/form.html'
    success_url = reverse_lazy('doctor-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['specializations'] = DoctorSpecialization.objects.all()
        return context

@method_decorator(login_required, name='dispatch')
class DoctorListView(ListView):
    model = DoctorProfile
    template_name = 'doctors/list.html'
    context_object_name = 'doctors'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user', 'branch').prefetch_related('specialization')

        # Filtering
        name = self.request.GET.get('name')
        branch = self.request.GET.get('branch')
        specialization = self.request.GET.get('specialization')

        if name:
            queryset = queryset.filter(user__name__icontains=name)
        if branch:
            queryset = queryset.filter(branch__id=branch)
        if specialization:
            queryset = queryset.filter(specialization__id=specialization)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['specializations'] = DoctorSpecialization.objects.all()
        return context


class WeeklyAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['created_at']  # Default ordering

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        queryset = WeeklyAvailability.objects.all()
        if doctor_id:
            # Custom ordering from Monday to Sunday

            queryset = queryset.filter(doctor_id=doctor_id)

        day_ordering = Case(
            *[When(day=day, then=pos) for pos, day in enumerate(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])]
        )
        return queryset.order_by(day_ordering)
        # return WeeklyAvailability.objects.none()

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            doctor_id = request.data[0].get('doctor') if request.data else None
            if doctor_id:
                WeeklyAvailability.objects.filter(doctor_id=doctor_id).delete()

            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-doctor/(?P<doctor_id>[^/.]+)')
    def by_doctor(self, request, doctor_id=None):
        availabilities = WeeklyAvailability.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(availabilities, many=True)
        return Response(serializer.data)


@login_required
def doctor_schedule(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    return render(request, 'doctors/schedule.html', {'doctor': doctor})
