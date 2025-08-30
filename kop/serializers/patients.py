from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.utils.crypto import get_random_string

from kop.models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by']





