from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps


def branch_admin_required(view_func):
    """
    Decorator that checks if the user is authenticated as a branch admin.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user has branch admin profile
        if not hasattr(request.user, 'branch_admin'):
            return render(request, '403.html', {
                'message': "Only branch-admins are allowed to access this page."
            }, status=403)

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def doctor_required(view_func):
    """Decorator to ensure only doctors can access the view."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Or your login URL

        # For DoctorProfile model approach
        if hasattr(request.user, 'doctor_profile'):
            return view_func(request, *args, **kwargs)

        return render(request, '403.html', {
            'message': "Only doctors are allowed to access this page."
        }, status=403)

    return _wrapped_view


from django.shortcuts import redirect, render


def superadmin_required(view_func):
    """Decorator to ensure only superadmins can access the view."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user is a superadmin (is_superuser flag)
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Render a custom 403 page
        return render(request, '403.html', {
            'message': "Only superadmins are allowed to access this page."
        }, status=403)

    return _wrapped_view


def doctor_or_superadmin_required(view_func):
    """Decorator to allow both doctors and superadmins to access the view."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user is a doctor or superadmin
        if hasattr(request.user, 'doctor_profile') or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Render a custom 403 page
        return render(request, '403.html', {
            'message': "Only doctors and administrators are allowed to access this page."
        }, status=403)

    return _wrapped_view


def branch_admin_or_superadmin_required(view_func):
    """Decorator to allow both doctors and superadmins to access the view."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user is a doctor or superadmin
        if hasattr(request.user, 'branch_admin') or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Render a custom 403 page
        return render(request, '403.html', {
            'message': "Only superadmin and administrators are allowed to access this page."
        }, status=403)

    return _wrapped_view
