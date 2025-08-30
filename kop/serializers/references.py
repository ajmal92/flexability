from rest_framework import serializers

from kop.models import Branch


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ['id', 'email', 'name']
