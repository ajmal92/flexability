from rest_framework.permissions import BasePermission
from kop.models import DoctorProfile


class DoctorModifyPermission(BasePermission):
    """Permission to check if user can modify doctors"""

    def has_permission(self, request, view):
        # Only allow superadmins and branch admins to modify doctors
        return request.user.is_superuser or hasattr(request.user, 'branch_admin_profile')

    def has_object_permission(self, request, view, obj):
        # Superadmins can modify any doctor
        if request.user.is_superuser:
            return True
        # Branch admins can only modify doctors in their branch
        if hasattr(request.user, 'branch_admin_profile'):
            return obj.branch in request.user.branch_admin_profile.branch
        return False


class DoctorViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        doctor_id = view.kwargs.get('pk')
        if doctor_id:
            doctor = DoctorProfile.objects.get(pk=doctor_id)
            if hasattr(request.user, 'branch_admin_profile'):
                return doctor.branch in request.user.branch_admin_profile.branch
            elif hasattr(request.user, 'doctor_profile'):
                return doctor.branch in request.user.doctor_profile.branch
            elif hasattr(request.user, 'staff_profile'):
                return doctor.branch in request.user.staff_profile.branch
        else:
            return True
