from rest_framework import serializers
from kop.models import WeeklyAvailability


class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyAvailability
        fields = ['id', 'email', 'name', 'is_active']


class WeeklyAvailabilityBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        return [self.child.create(attrs) for attrs in validated_data]


class WeeklyAvailabilitySerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = WeeklyAvailability
        fields = [
            'id',
            'doctor',
            'day',
            'day_display',
            'is_available',
            'login_time',
            'logout_time',
            'break_start_time',
            'break_end_time'
        ]

        list_serializer_class = WeeklyAvailabilityBulkSerializer

    def validate(self, data):
        if data.get('is_available', True):
            if not data.get('login_time') or not data.get('logout_time'):
                raise serializers.ValidationError(
                    "Login and logout times are required when available"
                )

            if data.get('login_time') and data.get('logout_time'):
                if data['login_time'] >= data['logout_time']:
                    raise serializers.ValidationError(
                        "Logout time must be after login time"
                    )

            if data.get('break_start_time') and data.get('break_end_time'):
                if data['break_start_time'] >= data['break_end_time']:
                    raise serializers.ValidationError(
                        "Break end time must be after break start time"
                    )
                if (data['break_start_time'] < data['login_time'] or
                    data['break_end_time'] > data['logout_time']):
                    raise serializers.ValidationError(
                        "Break time must be within working hours"
                    )
        return data
