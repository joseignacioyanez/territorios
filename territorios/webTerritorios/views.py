
import json
import os
from django import forms
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import SafeString
from django.views import View

from .models import Asignacion, Sordo, Publicador, Territorio, Congregacion, EstadoSordo
from .serializers import CongregacionSerializer, EstadoSordoSerializer, TerritorioSerializer, PublicadorSerializer, SordoSerializer, AsignacionSerializer
from rest_framework import viewsets
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from .scripts.territorioPDFdigital import llenarTerritorioDigital
from .scripts.territorioPDFimpreso import llenarTerritorioImpreso

import datetime


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

# Vista para obtener datos del usuario en base a su ID
# Usada en Bot de Telegram para validar permisos del Usuario en base a su grupos de permisos

# API
# Django REST Framework
class CongregacionViewSet(viewsets.ModelViewSet):
    queryset = Congregacion.objects.all()
    serializer_class = CongregacionSerializer

class EstadoSordoViewSet(viewsets.ModelViewSet):
    queryset = EstadoSordo.objects.all()
    serializer_class = EstadoSordoSerializer

class TerritorioViewSet(viewsets.ModelViewSet):
    queryset = Territorio.objects.all()
    serializer_class = TerritorioSerializer

    @action(detail=False, methods=['post'])
    def disponibles(self, request):
        data = request.data
        congregacion_id = data.get('congregacion_id')
        if congregacion_id is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Territorio.objects.filter(
                (Q(congregacion=congregacion_id) & ~Q(asignaciones_de_este_territorio__fecha_fin__isnull=True))
                |(Q(congregacion=congregacion_id) & Q(asignaciones_de_este_territorio__isnull=True))
                ).annotate(count=Count('asignaciones_de_este_territorio')).order_by('numero')
            serializer = TerritorioSerializer(queryset, many=True)
            return Response(serializer.data)

class PublicadorViewSet(viewsets.ModelViewSet):
    queryset = Publicador.objects.all()
    serializer_class = PublicadorSerializer

    @action(detail=False, methods=['post'])
    def buscar_telegram_chatid(self, request):
        data = request.data
        telegram_chatid = data.get('telegram_chatid')
        if telegram_chatid is None:
            return Response({'error': 'No se proporcionó el chat_id en la solicitud'}, status=400)
        else:
            queryset = Publicador.objects.filter(telegram_chatid=telegram_chatid)
            serializer = PublicadorSerializer(queryset, many=True)
            return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def activos_de_congregacion(self, request):
        data = request.data
        id_congregacion = data.get('congregacion_id')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Publicador.objects.filter(congregacion=id_congregacion, activo=True)
            serializer = PublicadorSerializer(queryset, many=True)
            return Response(serializer.data)

class SordoViewSet(viewsets.ModelViewSet):
    queryset = Sordo.objects.all()
    serializer_class = SordoSerializer

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()
    serializer_class = AsignacionSerializer

    @action(detail=False, methods=['post'])
    def pendientes(self, request):
        data = request.data
        id_congregacion = data.get('congregacion_id')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Asignacion.objects.filter(
                Q(territorio__congregacion=id_congregacion) & 
                Q(fecha_fin__isnull=True)
            )
            serializer = AsignacionSerializer(queryset, many=True)
            return Response(serializer.data)
        
def calcular_edad(anio_nacimiento):
    if anio_nacimiento is None:
        return 0
    else:
        
        return datetime.date.today().year - anio_nacimiento

from asgiref.sync import sync_to_async

@csrf_exempt
def asignar_territorio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            publicador_id = data.get('publicador_id')
            territorio_id = data.get('territorio_id')
            metodo_entrega = data.get('metodo_entrega')

            # Crear Asignacion
            publicador = Publicador.objects.get(pk=publicador_id)
            territorio = Territorio.objects.get(pk=territorio_id)
            asignacion = Asignacion(
                publicador=publicador,
                territorio=territorio,
            )
            asignacion.save()
            # Obtener Datos
            sordos = Sordo.objects.filter(territorio=territorio)
            territorio_nombre = str(territorio.numero) + ' - ' +  territorio.nombre
            id_asignacion = asignacion.id

            # Initialize variables
            texto1 = texto2 = texto3 = texto4 = texto5 = gps1 = gps2 = gps3 = gps4 = gps5 = id_sordo1 = id_sordo2 = id_sordo3 = id_sordo4 = id_sordo5 = ''

            # Check if sordos list has items
            if sordos:
                # Assign values if sordos list has items
                if len(sordos) > 0:
                    texto1 = sordos[0].nombre + " - " + str(calcular_edad(sordos[0].anio_nacimiento)) + ' años : ' + sordos[0].direccion + '\n' + sordos[0].detalles_direccion
                    gps1 = str(sordos[0].gps_latitud) + ',' + str(sordos[0].gps_longitud)
                    id_sordo1 = sordos[0].codigo
                if len(sordos) > 1:
                    texto2 = sordos[1].nombre + " - " + str(calcular_edad(sordos[1].anio_nacimiento)) + ' años : '  + sordos[1].direccion + '\n' + sordos[1].detalles_direccion
                    gps2 = str(sordos[1].gps_latitud) + ',' + str(sordos[1].gps_longitud)
                    id_sordo2 = sordos[1].codigo
                if len(sordos) > 2:
                    texto3 = sordos[2].nombre + " - " + str(calcular_edad(sordos[2].anio_nacimiento)) + ' años : ' + sordos[2].direccion + '\n' + sordos[2].detalles_direccion
                    gps3 = str(sordos[2].gps_latitud) + ',' + str(sordos[2].gps_longitud)
                    id_sordo3 = sordos[2].codigo
                if len(sordos) > 3:
                    texto4 = sordos[3].nombre + " - " + str(calcular_edad(sordos[3].anio_nacimiento)) + ' años : ' + sordos[3].direccion + '\n' + sordos[3].detalles_direccion
                    gps4 = str(sordos[3].gps_latitud) + ',' + str(sordos[3].gps_longitud)
                    id_sordo4 = sordos[3].codigo
                if len(sordos) > 4:
                    texto5 = sordos[4].nombre + " - " + str(calcular_edad(sordos[4].anio_nacimiento)) + ' años : ' + sordos[4].direccion + '\n' + sordos[4].detalles_direccion
                    gps5 = str(sordos[4].gps_latitud) + ',' + str(sordos[4].gps_longitud)
                    id_sordo5 = sordos[4].codigo

            script_dir = os.path.dirname(__file__)
            template = "scripts/recursos/plantillaDigitalNuevosBotones.pdf"
            template_impreso = "scripts/recursos/plantillaVaciaImprimir.pdf"
            boton1 = "scripts/recursos/botonGoogle.png"
            boton2 = "scripts/recursos/botonOsmand.png"
            boton_reportar = "scripts/recursos/botonReportar.png"
            boton_entregar = "scripts/recursos/botonTerminar.png"
            template = os.path.join(script_dir, template)
            template_impreso = os.path.join(script_dir, template_impreso)
            boton1 = os.path.join(script_dir, boton1)
            boton2 = os.path.join(script_dir, boton2)
            boton_reportar = os.path.join(script_dir, boton_reportar)
            boton_entregar = os.path.join(script_dir, boton_entregar)

            # Llenar y Enviar Territorio
            if metodo_entrega =='digital_publicador' or metodo_entrega == 'digital_asignador':
                file_path = llenarTerritorioDigital(texto1, texto2, texto3, texto4, texto5, territorio_nombre, gps1, gps2, gps3, gps4, gps5, id_sordo1, id_sordo2, id_sordo3, id_sordo4, id_sordo5, id_asignacion, template, boton1, boton2, boton_reportar, boton_entregar)
                return JsonResponse({'chat_id': publicador.telegram_chatid, 'file_path': file_path, 'territorio':territorio_nombre}, status=200)
                
            elif metodo_entrega == 'impreso_asignador':
                file_path = llenarTerritorioImpreso(texto1, texto2, texto3, texto4, texto5, territorio_nombre, gps1, gps2, gps3, gps4, gps5, id_sordo1, id_sordo2, id_sordo3, id_sordo4, id_sordo5, template_impreso)
                return JsonResponse({'file_path': file_path, 'territorio':territorio_nombre}, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
