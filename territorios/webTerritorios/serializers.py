from .models import Congregacion, EstadoSordo, Territorio, Publicador, Sordo, Asignacion
from rest_framework import serializers
from django.contrib.auth.models import Group, User

class CongregacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Congregacion
        fields = '__all__'

class EstadoSordoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoSordo
        fields = '__all__'

class TerritorioSerializer(serializers.ModelSerializer):
    congregacion_nombre = serializers.CharField(source='congregacion.nombre', read_only=True)

    class Meta:
        model = Territorio
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups', 'is_staff', 'is_superuser')

class PublicadorSerializer(serializers.ModelSerializer):
    congregacion_nombre = serializers.CharField(source='congregacion.nombre', read_only=True)
    user = UserSerializer()

    class Meta:
        model = Publicador
        fields = '__all__'

class SordoSerializer(serializers.ModelSerializer):
    congregacion_nombre = serializers.CharField(source='congregacion.nombre', read_only=True)
    territorio_numero = serializers.IntegerField(source='territorio.numero', read_only=True)
    territorio_nombre = serializers.CharField(source='territorio.nombre', read_only=True)
    estado_sordo_texto = serializers.CharField(source='estado_sordo.nombre', read_only=True)

    class Meta:
        model = Sordo
        fields = '__all__'

class AsignacionSerializer(serializers.ModelSerializer):
    publicador_nombre = serializers.CharField(source='publicador.nombre', read_only=True)
    territorio_numero = serializers.IntegerField(source='territorio.numero', read_only=True)
    territorio_nombre = serializers.CharField(source='territorio.nombre', read_only=True)

    class Meta:
        model = Asignacion
        fields = '__all__'
