from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from.models import *


class SordoAdmin(admin.ModelAdmin):
    # Mostrar campos como TextArea
    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'descripcion':forms.Textarea,
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
admin.site.register(Genero)
admin.site.register(SeniasTipo)
admin.site.register(EstadoSordo)
admin.site.register(Territorio)
admin.site.register(Asignacion)
admin.site.register(Log)
admin.site.register(TipoLog)