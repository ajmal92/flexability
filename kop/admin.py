from django.contrib import admin

# Register your models here.
from .models import *

# admin.site.register(User)
# admin.site.register(DoctorProfile)
admin.site.register(DoctorSpecialization)
# admin.site.register(BranchAdmin)
admin.site.register(WeeklyAvailability)
admin.site.register(TreatmentSession)
admin.site.register(PatientWeeklySchedule)
admin.site.register(PatientTreatment)
admin.site.register(PatientAttachment)
admin.site.register(PatientConsultation)
admin.site.register(Invoice)
admin.site.register(Payment)
#
from django.contrib import admin
from .models import DoctorProfile


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    # Fields to display in list view
    list_display = ('name','phone_number', 'email', 'is_active')

    # Fields to show in edit view
    fieldsets = (
        (None, {'fields': ('name','address','phone_number', 'email', 'is_active' )}),  # Your regular fields
        ('Audit Information', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )

    # Make audit fields read-only
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    # Add filters for audit fields
    list_filter = ('created_at', 'updated_at')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    # Fields to display in list view
    list_display = ('user',)

    # Fields to show in edit view
    fieldsets = (
        (None, {'fields': ('user','specialization','license_number','branch', 'phone_number' )}),  # Your regular fields
        ('Audit Information', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )

    # Make audit fields read-only
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    # Add filters for audit fields
    list_filter = ('created_at', 'updated_at')

