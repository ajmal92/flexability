from django.contrib.auth.mixins import LoginRequiredMixin


class LoginRequiredMixIn(LoginRequiredMixin):
    login_url = '/login/'  # Specify your login URL
    redirect_field_name = 'next'  # Default is 'next'
