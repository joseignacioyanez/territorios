from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse, reverse_lazy
from django.utils.safestring import SafeString
from .models import Sordo
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.contrib import messages


class TerritoriosLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('webTerritorios:index') 
    
    def form_invalid(self, form):
        messages.error(self.request,'Usuario o Contraseña incorrectos')
        return self.render_to_response(self.get_context_data(form=form))



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
    

def index(request):
    return render(request, "webTerritorios/index.html", {
        "sordos": Sordo.objects.all()
    })

def sordo(request, congregacion, codigo):
    sordo = Sordo.objects.get(codigo=codigo, territorio__congregacion__id=congregacion)
    return render(request, "webTerritorios/detalleSordo.html", {
        "sordo": sordo,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

def addSordo(request):
    if request.method == "POST":
        form = NewSordoForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            direccion = form.cleaned_data["direccion"]
            edad = form.cleaned_data["edad"]
            newSordo = Sordo.objects.create(name=name, direccion=direccion, edad=edad)
            return HttpResponseRedirect(reverse("webTerritorios:index"))
        else:
            return render(request, "webTerritorios/addSordo.html", {
                "form": form
            })

    return render(request, "webTerritorios/addSordo.html", {
        "form": NewSordoForm()
    })

def editSordo(request, id):

    sordo = Sordo.objects.get(pk=id)
    form = NewSordoForm(instance=sordo)
    if request.method == "POST":
        form = NewSordoForm(request.POST, instance=sordo)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("webTerritorios:index"))
    
    context = {'form': form}
    return render(request, 'webTerritorios/editSordo.html', context)

def deleteSordo(request, id):
    sordo = Sordo.objects.get(pk=id)
    if request.method == "POST":
        sordo.delete()
        return HttpResponseRedirect(reverse("webTerritorios:index"))
    context = {'sordo': sordo}
    return render(request, 'webTerritorios/deleteSordo.html', context)

