from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin  # type: ignore
from leaflet_point.admin import LeafletPointAdmin # type: ignore

from.models import *

SUPERUSUARIO_GLOBAL = "joseignacio" # Mi usuario lo puede ver Todo 👀

class GrupoFilter(admin.SimpleListFilter):
    title = 'Grupo'
    parameter_name = 'grupo'

    def lookups(self, request, model_admin):
        grupos = Group.objects.all()
        return [(g.name, g.name) for g in grupos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__name=self.value())
        return queryset

class VerSoloMiCongregacionFilter(admin.SimpleListFilter):
    title = 'Ver solo mi congregación'
    parameter_name = 'scope'

    def lookups(self, request, model_admin):
        if request.user.username == SUPERUSUARIO_GLOBAL:
            return (
                ('local', 'Solo mi congregación'),
                ('global', 'Ver todo'),
            )
        return []
    
    def queryset(self, request, queryset):
        if request.user.username != SUPERUSUARIO_GLOBAL:
            return queryset
        
        scope = self.value() or 'local'

        if scope == 'local':
            if hasattr(request.user, "publicador") and request.user.publicador.congregacion:
                return queryset.filter(congregacion=request.user.publicador.congregacion)
        return queryset

class FiltroPorCongregacionMixin:
    """Mixin para filtrar por congregación (salvo para SUPERUSUARIO_GLOBAL)."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username == SUPERUSUARIO_GLOBAL:
            if request.GET.get('scope') == 'local':
                if hasattr(request.user, "publicador") and request.user.publicador.congregacion:
                    return qs.filter(congregacion=request.user.publicador.congregacion)
            return qs
        if hasattr(request.user, "publicador") and request.user.publicador.congregacion:
            return qs.filter(congregacion=request.user.publicador.congregacion)
        return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user = request.user
        if user.username != SUPERUSUARIO_GLOBAL and hasattr(user, "publicador"):
            cong = user.publicador.congregacion
            if db_field.name == "congregacion":
                kwargs["queryset"] = Congregacion.objects.filter(pk=cong.pk)
            elif db_field.name in ["territorio", "publicador"]:
                kwargs["queryset"] = db_field.related_model.objects.filter(congregacion=cong)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CustomLeafletPointAdmin(LeafletPointAdmin):
    list_display = ('{title/name/...}', 'gps_latitud', 'gps_longitud')

class SordoAdmin(FiltroPorCongregacionMixin, ImportExportModelAdmin, LeafletPointAdmin, admin.ModelAdmin, ):
    exclude = ('codigo', 'local_id')
    ordering = ('codigo',)
    list_filter = ('congregacion', 'estado_sordo', VerSoloMiCongregacionFilter, 'territorio', 'publicador_estudio')

    fieldsets = (
        ('Información Básica - (Sale en Tarjetas)', {
            'fields': ('congregacion', 'nombre', 'territorio', 'direccion', 'detalles_direccion', 'mejorVisitar', 'estado_sordo', 'publicador_estudio')
        }),
        ('Información Antigua - (No Sale en Tarjetas)', {
            'fields': ('tipo_senias', 'anio_nacimiento', 'telefono', 'detalles_sordo', 'detalles_familia')
        }),
        ('Ubicación GPS - (Ingrese en formato Decimal [-0.123456] o use el Pin en el Mapa)', {
            'fields': ('gps_latitud', 'gps_longitud')
        }),
    )

    # Mostrar campos como TextArea
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'detalles_familia':forms.Textarea,
            'detalles_sordo':forms.Textarea,
            'detalles_direccion':forms.Textarea,
            'direccion': forms.Textarea,
            }
        return super().get_form(request, obj, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user = request.user
        if user.username != SUPERUSUARIO_GLOBAL :
            cong = user.publicador.congregacion
            if db_field.name == "congregacion":
                kwargs["queryset"] = Congregacion.objects.filter(pk=cong.pk)
            elif db_field.name in ["territorio", "publicador_estudio"]:
                kwargs["queryset"] = db_field.related_model.objects.filter(congregacion=cong)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Territorio, site=admin.site)
class TerritorioAdmin(FiltroPorCongregacionMixin, ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'congregacion')
    list_filter = (VerSoloMiCongregacionFilter, 'congregacion', 'activo')
    

class PublicadorInline(FiltroPorCongregacionMixin, admin.StackedInline):
    model = Publicador
    can_delete = False
    verbose_name_plural = 'Publicadores'
    fk_name = 'user'   # indica que la FK en Publicador es `user`
    # Si quisieras filtrar los publicadores mostrados según la congregación,
    # tu mixin `formfield_for_foreignkey` ya lo haría cuando haya campos FK,
    # pero para el inline normalmente no es necesario más.

# Re-register UserAdmin
admin.site.unregister(User)
@admin.register(User)  # o bien usa admin.site.unregister/ register como tenías
class UserAdmin(BaseUserAdmin):

    # Mostrar Grupos
    def es_superadmin(self, obj):
        return obj.groups.filter(name='superadministradores').exists()
    es_superadmin.boolean = True  # muestra como ✔/✘
    es_superadmin.short_description = 'Superadmin'

    def es_admin(self, obj):
        return obj.groups.filter(name='administradores').exists()
    es_admin.boolean = True
    es_admin.short_description = 'Admin'

    def es_asignador(self, obj):
        return obj.groups.filter(name='asignadores').exists()
    es_asignador.boolean = True
    es_asignador.short_description = 'Asignador'

    inlines = [PublicadorInline]
    list_filter = ('publicador__congregacion', GrupoFilter, 'publicador__activo', 'is_staff')
    list_display = ('username', 'is_staff', 'es_superadmin', 'es_admin', 'es_asignador')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Grupos y Permisos', {'fields': ('groups',)}),
        ('Permisos Granulares - (Solo usar Grupos)', {'classes': ('expanded', 'collapse' ,'collapsed') ,'fields': ('user_permissions',)}),
        ('Fechas Importantes - (No necesario modificar)', {'classes': ('expanded', 'collapse' ,'collapsed') ,'fields': ('last_login',)}),
        ('Información Personal - (No necesario modificar)', {'classes': ('expanded', 'collapse' ,'collapsed') , 'fields': ('first_name', 'last_name', 'email')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Filtrado por congregación (si no es superusuario global)
        if request.user.username != SUPERUSUARIO_GLOBAL:
            qs = qs.filter(publicador__congregacion=request.user.publicador.congregacion)

        return qs

@admin.register(Asignacion)
class AsignacionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('publicador', 'territorio_nombre_texto', 'fecha_asignacion', 'fecha_fin')
    list_filter = ('publicador__congregacion', 'publicador', 'territorio')

    # Dont show field on form
    exclude = ('territorio_numero_texto', 'territorio_nombre_texto')

    def get_queryset(self, request):
        # Llamamos directamente al get_queryset de ModelAdmin (sin pasar por el mixin)
        qs = admin.ModelAdmin.get_queryset(self, request)
        if request.user.username == SUPERUSUARIO_GLOBAL:
            return qs
        # filtramos por territorio__congregacion
        return qs.filter(territorio__congregacion=request.user.publicador.congregacion)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user = request.user
        if user.username != SUPERUSUARIO_GLOBAL:
            cong = user.publicador.congregacion
            if db_field.name == "territorio":
                kwargs["queryset"] = db_field.related_model.objects.filter(congregacion=cong)
            elif db_field.name == "publicador":
                kwargs["queryset"] = db_field.related_model.objects.filter(congregacion=cong)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Congregacion, site=admin.site)
class CongregacionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.username == SUPERUSUARIO_GLOBAL:
            return qs
        if hasattr(request.user, "publicador"):
            return qs.filter(pk=request.user.publicador.congregacion.pk)
        return qs.none()

# Register your models here.
admin.site.register(Sordo, SordoAdmin,config_overrides = {
        'lat_input_selector': 'gps_latitud', # if you want to name your field differently
        'lng_input_selector': 'gps_longitud', # defaults to longitude and latitude
        'map_height': 500, # defaults to 400
        'geocoder': True # defaults to false
    }  )

# 1) Primero, quitas el registro por defecto
admin.site.unregister(Group)

# 2) Registras tu propia versión de GroupAdmin
@admin.register(Group)
class GroupAdmin(DefaultGroupAdmin):
    def get_model_perms(self, request):
        """
        Devuelve {} (sin permisos) para que el modelo no aparezca
        en el índice de la admin para usuarios distintos de SUPERUSUARIO_GLOBAL.
        """
        if request.user.username == SUPERUSUARIO_GLOBAL:
            # Para ti, deja los permisos de siempre (view/add/change/delete)
            return super().get_model_perms(request)
        # Para cualquier otro usuario: ni ver, ni añadir, ni cambiar, ni borrar
        return {}

    def has_view_permission(self, request, obj=None):
        # Asegura que ni siquiera aludir directamente a la URL permita verlo
        return request.user.username == SUPERUSUARIO_GLOBAL

    def has_change_permission(self, request, obj=None):
        return request.user.username == SUPERUSUARIO_GLOBAL

    def has_add_permission(self, request):
        return request.user.username == SUPERUSUARIO_GLOBAL

    def has_delete_permission(self, request, obj=None):
        return request.user.username == SUPERUSUARIO_GLOBAL


admin.site.site_header = "Administración de Territorios"
admin.site.site_title = "Administración de Territorios"
admin.site.index_title = "Bienvenido, seleccione una opción"