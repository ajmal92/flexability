from rest_framework import serializers
from kop.models import TreatmentProgram

class TreatmentProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentProgram
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at','created_by','updated_by')


class TreatmentProgramListSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentProgram
        fields = ['id', 'name', 'rate_per_session', 'default_duration',
                 'branch_name', 'doctor_count', 'created_at']
        read_only_fields = ('created_at', 'updated_at','created_by','updated_by')

    def get_doctor_count(self, obj):
        return obj.doctors.count()
