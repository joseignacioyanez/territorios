from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from.models import *


class SordoAdmin(admin.ModelAdmin):
    exclude = ('codigo', 'local_id')

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
    

# Manejar Publicador como extension de User
class PublicadorInline(admin.StackedInline):
    model = Publicador
    can_delete = False
    verbose_name_plural = 'Publicadores'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [PublicadorInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(Sordo, SordoAdmin)
admin.site.register(Congregacion)
admin.site.register(EstadoSordo)
admin.site.register(Territorio)
admin.site.register(Asignacion)