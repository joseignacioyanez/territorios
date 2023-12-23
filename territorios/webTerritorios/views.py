from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.utils.safestring import SafeString
from .models import Sordo


sordos = ["German", "Mely", "Pepe"]

class NewSordoForm(forms.ModelForm):

    class Meta:

        model = Sordo
        fields = ["name", "direccion", "edad"]
        name = forms.CharField(label="Nombre")
        direccion = forms.CharField(label="Direccion")
        edad = forms.IntegerField(label="Edad")
        
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

