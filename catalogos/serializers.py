from rest_framework import serializers
from .models import Departamento, Puesto

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        read_only_fields = ('id','created_at','updated_at')

class PuestoSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)

    class Meta:
        model = Puesto
        fields = '__all__'
        read_only_fields = ('id','created_at','updated_at')
