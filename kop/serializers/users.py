from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.utils.crypto import get_random_string


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name']

    def create(self, validated_data):
        password = get_random_string(15)
        validated_data.pop('created_by', None)
        validated_data['is_active']=True
        print(validated_data)
        user = get_user_model().objects.create(**validated_data, is_staff=True)
        user.set_password(password)
        user.save()
        return user





