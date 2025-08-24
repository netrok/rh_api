from rest_framework import serializers
from .models import Empleado

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'
        read_only_fields = ('id','created_at','updated_at')

    def validate_curp(self, v): return v.strip().upper()
    def validate_rfc(self, v):  return v.strip().upper()
