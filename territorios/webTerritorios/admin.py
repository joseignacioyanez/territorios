from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin  # type: ignore
from leaflet_point.admin import LeafletPointAdmin # type: ignore

from.models import *

class CustomLeafletPointAdmin(LeafletPointAdmin):
    list_display = ('{title/name/...}', 'gps_latitud', 'gps_longitud')

class SordoAdmin(ImportExportModelAdmin, LeafletPointAdmin):
    exclude = ('codigo', 'local_id')
    ordering = ('codigo',)
    list_filter = ('congregacion', 'estado_sordo', 'territorio', 'publicador_estudio')

    # Mostrar campos como TextArea
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'detalles_familia':forms.Textarea,
            'detalles_sordo':forms.Textarea,
            'detalles_direccion':forms.Textarea,
            'direccion': forms.Textarea,
            }
        return super().get_form(request, obj, **kwargs)
    
class TerritorioAdmin(ImportExportModelAdmin):
    list_display = ('numero', 'nombre', 'congregacion')
    

# Manejar Publicador como extension de User
class PublicadorInline(admin.StackedInline):
    model = Publicador
    can_delete = False
    verbose_name_plural = 'Publicadores'

class AsignacionAdmin(ImportExportModelAdmin):
    list_display = ('publicador', 'territorio', 'fecha_asignacion', 'fecha_fin')

# Define a new User admin
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    list_filter = ('is_staff', 'publicador__congregacion', 'publicador__activo')
    list_display = ('username', 'is_staff')
    inlines = [PublicadorInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(Sordo, SordoAdmin,config_overrides = {
        'lat_input_selector': 'gps_latitud', # if you want to name your field differently
        'lng_input_selector': 'gps_longitud', # defaults to longitude and latitude
        'map_height': 500, # defaults to 400
        'geocoder': True # defaults to false
    }  )
admin.site.register(Congregacion)
admin.site.register(EstadoSordo)
admin.site.register(Territorio, TerritorioAdmin)
admin.site.register(Asignacion, AsignacionAdmin)