# views.py
from django.views import View
from django.shortcuts import redirect


def login_redirect(request):
    """
    Redirect users to different pages based on their profile after login.
    """
    # Check if user is authenticated (should be after login)
    if request.user.is_authenticated:
        # Check user type and redirect accordingly
        if hasattr(request.user, 'doctor_profile'):
            return redirect('doctor_dashboard')
        elif hasattr(request.user, 'branch_admin'):
            return redirect('branch_admin_dashboard')
        elif request.user.is_superuser or request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            # Default redirect for users without specific profiles
            return redirect('home')
    else:
        # If not authenticated, redirect to the actual login page
        return redirect('/accounts/login/')


