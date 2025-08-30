from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views
from .forms.treatment_session import PatientTreatmentAutocomplete
from .serializers.references import BranchSerializer
from .views.attendance import doctor_dashboard, mark_attendance, PatientAutocomplete, complete_consultation
from .views.branch_admin import BranchAdminListView, BranchAdminDetailView, BranchAdminCreateView, \
    BranchAdminUpdateView, BranchAdminDeleteView, branch_admin_dashboard
from .views.consultation import PatientConsultationListView, PatientConsultationCreateView, \
    PatientConsultationDetailView, PatientConsultationUpdateView, PatientConsultationDeleteView
from .views.doctorprofile import doctor_schedule, WeeklyAvailabilityViewSet, DoctorCreateView, \
    DoctorListView, DoctorUpdateView, DoctorDetailView
from .views.invoice import InvoiceListView, InvoiceDetailView
from .views.login import login_redirect
from .views.patient_attachment import create_patient_attachment, PatientAttachmentUpdateView, download_attachment, \
    PatientAttachmentDeleteView
from .views.patient_treatment import PatientTreatmentCreateView, PatientTreatmentUpdateView, PatientTreatmentListView, \
    PatientTreatmentDetailView
from .views.patient_weekly_schedule import PatientWeeklyScheduleListView, PatientWeeklyScheduleCreateView, \
    PatientWeeklyScheduleUpdateView, PatientWeeklyScheduleDeleteView
from .views.patients import PatientViewSet, patient_detail, patient_update, patient_delete
from .views.payments import CreatePaymentView
from .views.references import LeadSourceListView, LeadSourceCreateView, LeadSourceDetailView, LeadSourceUpdateView, \
    LeadSourceDeleteView, BranchListView, BranchCreateView, BranchDetailView, BranchUpdateView, BranchDeleteView, \
    DoctorSpecializationListView, DoctorSpecializationCreateView, DoctorSpecializationDetailView, \
    DoctorSpecializationUpdateView, DoctorSpecializationDeleteView
from .views.test import test_view
from .views.treatment_program import TreatmentProgramViewSet, TreatmentProgramListView, TreatmentProgramCreateView, \
    TreatmentProgramUpdateView, TreatmentProgramDeleteView
from .views.treatment_session import TreatmentSessionListView, TreatmentSessionCreateView, SessionDetailView, \
    SessionUpdateView, TreatmentSessionDeleteView
from .views.users import UserProfileViewSet
from kop.views.patients import patient_list, add_patient
from django.views.generic import RedirectView


# API Router
router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='users')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'availability', WeeklyAvailabilityViewSet, basename='availability')
router.register(r'treatment-programs', TreatmentProgramViewSet, basename='treatment_programs')

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Authentication
    # path('login/', RedirectView.as_view(url='/accounts/login/', permanent=True), name='login'),
    path('login/', login_redirect, name='login'),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Doctors
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/create/', DoctorCreateView.as_view(), name='doctor-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('doctors/<int:pk>/edit/', DoctorUpdateView.as_view(), name='doctor-edit'),
    path('doctors/<int:doctor_id>/schedule/', doctor_schedule, name='doctor-schedule'),

    # Patients
    path('patients/', patient_list, name='patient-list'),
    path('patients/add', add_patient, name='patient-add'),
    path('patients/<int:pk>/', patient_detail, name='patient-detail'),
    path('patients/<int:pk>/update/', patient_update, name='patient-update'),
    path('patients/<int:pk>/delete', patient_delete, name='patient-delete'),
    path('patient-autocomplete/', PatientAutocomplete.as_view(), name='patient-autocomplete'),
    path('patients/<int:patient_id>/consultations/create/',
         PatientConsultationCreateView.as_view(),
         name='consultation-create'),

    # Patient Attachments
    path('patients/<int:patient_id>/attachment/add/', create_patient_attachment, name='add_patient_attachment'),
    path('attachment/<int:pk>/edit/', PatientAttachmentUpdateView.as_view(), name='edit_patient_attachment'),
    path('attachment/<int:attachment_id>/download/', download_attachment, name='download_attachment'),
    path('attachment/<int:pk>/delete/', PatientAttachmentDeleteView.as_view(), name='delete_patient_attachment'),

    # Patient Weekly Schedules
    path('patients/<int:patient_id>/schedules/', PatientWeeklyScheduleListView.as_view(),
         name='patient-weekly-schedule-list'),
    path('patients/<int:patient_id>/schedules/create/', PatientWeeklyScheduleCreateView.as_view(),
         name='patient-weekly-schedule-create'),
    path('schedules/<int:pk>/edit/', PatientWeeklyScheduleUpdateView.as_view(), name='patient-weekly-schedule-edit'),
    path('schedules/<int:pk>/delete/', PatientWeeklyScheduleDeleteView.as_view(),
         name='patient-weekly-schedule-delete'),

    # Treatment Programs
    path('treatment-programs/', TreatmentProgramListView.as_view(), name='treatment-program-list'),
    path('treatment-programs/create/', TreatmentProgramCreateView.as_view(), name='treatment-program-create'),
    path('treatment-programs/<int:pk>/edit/', TreatmentProgramUpdateView.as_view(), name='treatment-program-edit'),
    path('treatment-programs/<int:pk>/delete/', TreatmentProgramDeleteView.as_view(), name='treatment-program-delete'),
    path('treatment-programs/auto-complete/', PatientTreatmentAutocomplete.as_view(),
         name='treatment-program-autocomplete'),

    # Patient Treatments
    path('patient-treatment/', PatientTreatmentListView.as_view(), name='patient-treatment-list'),
    path('patient-treatment/create/', PatientTreatmentCreateView.as_view(), name='patient-treatment-create'),
    path('patients/<int:patient_id>/patient-treatment/create/', PatientTreatmentCreateView.as_view(),
         name='patient-treatment-create'),
    path('patient-treatment/<int:pk>/edit/', PatientTreatmentUpdateView.as_view(), name='patient-treatment-edit'),
    path('patient-treatment/<int:pk>/detail/', PatientTreatmentDetailView.as_view(), name='patient-treatment-detail'),

    # Treatment Sessions
    path('treatment_sessions/', TreatmentSessionListView.as_view(), name='treatment-session-list'),
    path('treatment_sessions/create/', TreatmentSessionCreateView.as_view(), name='treatment-session-create'),
    path('patients/<int:patient_id>/treatment_sessions/create/', TreatmentSessionCreateView.as_view(),
         name='treatment-session-create-for-patient'),
    path('treatment_sessions/<int:pk>/', SessionDetailView.as_view(), name='treatment-session-detail'),
    path('treatment_sessions/<int:pk>/edit/', SessionUpdateView.as_view(), name='treatment-session-edit'),
    path('treatment_sessions/<int:pk>/delete/', TreatmentSessionDeleteView.as_view(), name='treatment-session-delete'),

    # Attendance
    path('doctors/dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('session/mark-attendance/', mark_attendance, name='mark_attendance'),
    path('session/<int:session_id>/mark-attendance/', mark_attendance, name='mark_attendance'),

    # Consultations
    path('consultations/', PatientConsultationListView.as_view(), name='consultation-list'),
    path('consultations/create/patient/<int:patient_id>/', PatientConsultationCreateView.as_view(),
         name='consultation-create'),
    path('consultations/create/', PatientConsultationCreateView.as_view(), name='consultation-create'),
    path('consultations/<int:pk>/', PatientConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/<int:pk>/update/', PatientConsultationUpdateView.as_view(), name='consultation-update'),
    path('consultations/<int:pk>/delete/', PatientConsultationDeleteView.as_view(), name='consultation-delete'),
    path('consultations/<int:pk>/complete/', complete_consultation, name='complete_consultation'),

    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoice/<int:invoice_id>/payment/create/', CreatePaymentView.as_view(), name='create_payment'),


    # References
    # Lead Sources
    path('leadsources/', LeadSourceListView.as_view(), name='leadsource-list'),
    path('leadsources/create/', LeadSourceCreateView.as_view(), name='leadsource-create'),
    path('leadsources/<int:pk>/', LeadSourceDetailView.as_view(), name='leadsource-detail'),
    path('leadsources/<int:pk>/update/', LeadSourceUpdateView.as_view(), name='leadsource-update'),
    path('leadsources/<int:pk>/delete/', LeadSourceDeleteView.as_view(), name='leadsource-delete'),

    # Branches
    path('branches/', BranchListView.as_view(), name='branch-list'),
    path('branches/create/', BranchCreateView.as_view(), name='branch-create'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),
    path('branches/<int:pk>/update/', BranchUpdateView.as_view(), name='branch-update'),
    path('branches/<int:pk>/delete/', BranchDeleteView.as_view(), name='branch-delete'),

    # Doctor Specializations
    path('specializations/', DoctorSpecializationListView.as_view(), name='doctorspecialization-list'),
    path('specializations/create/', DoctorSpecializationCreateView.as_view(), name='doctorspecialization-create'),
    path('specializations/<int:pk>/', DoctorSpecializationDetailView.as_view(), name='doctorspecialization-detail'),
    path('specializations/<int:pk>/update/', DoctorSpecializationUpdateView.as_view(),
         name='doctorspecialization-update'),
    path('specializations/<int:pk>/delete/', DoctorSpecializationDeleteView.as_view(),
         name='doctorspecialization-delete'),

    # Branch Admin URLs
    path('branch-admins/', BranchAdminListView.as_view(), name='branch_admin_list'),
    path('branch-admins/<int:pk>/', BranchAdminDetailView.as_view(), name='branch_admin_detail'),
    path('branch-admins/add/', BranchAdminCreateView.as_view(), name='branch_admin_create'),
    path('branch-admins/<int:pk>/edit/', BranchAdminUpdateView.as_view(), name='branch_admin_update'),
    path('branch-admins/<int:pk>/delete/', BranchAdminDeleteView.as_view(), name='branch_admin_delete'),
    path('branch-admins/dashboard/', branch_admin_dashboard, name='branch_admin_dashboard'),

    path('accounts/', include('allauth.urls')),


    path('test/', test_view),
]
