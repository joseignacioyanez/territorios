
import datetime
from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import SafeString
from django.views import View
from .models import Sordo, Publicador, Territorio
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.db.models import Q


class TerritoriosLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('webTerritorios:menu') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Usuario o Contraseña incorrectos')
        return self.render_to_response(self.get_context_data(form=form))
    
def logoutView(request):
    logout(request)
    return redirect(reverse("login"))

class MenuView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")

    def get(self, request):
        user_groups = request.user.groups.all()  
        return render(request, "webTerritorios/menu.html", {"user_groups": user_groups})

class AsignarView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")

    def get(self, request):
        congregacion = request.user.publicador.congregacion
        publicadores = Publicador.objects.filter(congregacion=congregacion, activo=True)
        territorios = Territorio.objects.filter(
            Q(congregacion=congregacion) & 
            (Q(asignaciones_de_este_territorio__fecha_fin__isnull=False) | Q(asignaciones_de_este_territorio__isnull=True))
        )

        return render(request, "webTerritorios/asignar.html", {
            "publicadores": publicadores,
            "territorios": territorios,
        })
    
    def post(self, request):
        if request.POST.get('enviarTelegram'):
            print("Enviar Telegram")
            pass
        elif request.POST.get('registrarPDFdigital'):
            print("Registrar PDF Digital")
            pass
        elif request.POST.get('registrarPDFimprimir'):
            print("Registrar PDF Imprimir")
            pass
        
        return redirect(reverse("webTerritorios:asignar"))

class NewSordoForm(forms.ModelForm):

    class Meta:

        model = Sordo
        fields = ["nombre", "direccion", "anio_nacimiento"]
        nombre = forms.CharField(label="Nombre")
        direccion = forms.CharField(label="Direccion")
        anio_nacimiento = forms.IntegerField(label="Año de Nacimiento")
        
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "edad": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 80})
        }

        def as_div(self):
            return SafeString(super().as_div().replace("<div>", "<div class='form-group mb-3'>"))
    
