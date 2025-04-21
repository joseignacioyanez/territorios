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
    cantidad_sordos = serializers.IntegerField(source='sordos.count', read_only=True)
    # Revisar si existen asignaciones cuya fecha_fin sea null
    asignado = serializers.SerializerMethodField(read_only=True)
    def get_asignado(self, obj):
        return obj.asignaciones_de_este_territorio.filter(fecha_fin__isnull=True).exists()

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
    congregacion_id = serializers.IntegerField(source='congregacion.id', read_only=True)
    user = UserSerializer()

    class Meta:
        model = Publicador
        fields = '__all__'

class UserConPublicadorSerializer(UserSerializer):
    congregacion_id = serializers.IntegerField(source='congregacion.id', read_only=True)
    congregacion_nombre = serializers.CharField(source='congregacion.nombre', read_only=True)
    nombre = serializers.CharField(read_only=True)
    telegram_chatid = serializers.CharField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'congregacion_id',
            'congregacion_nombre',
            'nombre',
            'telegram_chatid',
        )

class PublicadorExtendidoSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Publicador
        fields = ('user',)

    def get_user(self, obj):
        from django.contrib.auth.models import Group

        user = obj.user

        # Obtenemos grupos con nombre e ID
        groups = [
            {"id": group.id, "name": group.name}
            for group in user.groups.all()
        ]

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "groups": groups,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,

            # Extra: Campos del Publicador
            "nombre": obj.nombre,
            "telegram_chatid": obj.telegram_chatid,
            "congregacion_id": obj.congregacion.id if obj.congregacion else None,
            "congregacion_nombre": obj.congregacion.nombre if obj.congregacion else None,
        }


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
