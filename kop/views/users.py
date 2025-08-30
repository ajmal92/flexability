# api/views.py
from django.contrib.auth import get_user_model

from kop.models import WeeklyAvailability
from kop.serializers.doctorprofile import WeeklyAvailabilitySerializer
from kop.serializers.users import UserSerializer


from kop.views.doctorprofile import SerializerBase

User = get_user_model()


class UserProfileViewSet(SerializerBase):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()

        if self.request.user.is_superuser or hasattr(self.request.user, 'branch_admin_profile'):
            return queryset

        return User.objects.none()



