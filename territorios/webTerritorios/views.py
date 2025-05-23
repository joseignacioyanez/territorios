
import base64
import json
import os
import threading
import time
from django import forms
from django.http import FileResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import SafeString
from django.views import View
import pandas as pd
import requests

from .models import Asignacion, Sordo, Publicador, Territorio, Congregacion, EstadoSordo
from .serializers import CongregacionSerializer, EstadoSordoSerializer, PublicadorExtendidoSerializer, TerritorioSerializer, PublicadorSerializer, SordoSerializer, AsignacionSerializer 
from rest_framework import viewsets
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.messages import get_messages


from .scripts.territorioPDFdigital import llenarTerritorioDigital
from .scripts.territorioPDFimpreso import llenarTerritorioImpreso

import datetime

# No vista, Funcion de ayuda
def preparar_y_generar_territorio(publicador_id, territorio_id, metodo_entrega, solo_pdf):

    publicador = Publicador.objects.get(pk=publicador_id)
    territorio = Territorio.objects.get(pk=territorio_id)
    
    # Si es asignacion nueva, guardar en BD
    if not solo_pdf:
        asignacion = Asignacion(
            publicador=publicador,
            territorio=territorio,
        )
        asignacion.save()
    else:
        asignacion = Asignacion.objects.filter(publicador=publicador, territorio=territorio).last()
    
    # Generar PDF Territorio
    # Obtener Datos
    sordos = Sordo.objects.filter(territorio=territorio)
    territorio_nombre = str(territorio.numero) + ' - ' +  territorio.nombre
    id_asignacion = asignacion.id

    # Initialize variables
    texto1 = texto2 = texto3 = texto4 = texto5 = gps1 = gps2 = gps3 = gps4 = gps5 = id_sordo1 = id_sordo2 = id_sordo3 = id_sordo4 = id_sordo5 = ''

    # Check if sordos list has items
    datos = []
    if sordos:
        # Asignar valores en el formato que se usa en la generacion del territori
        # Texto: Direccion y Detalles de Direccion (No nombre ni edad)
        # GPS: "Latitud,Longitud"
        # ID: Codigo del Sordo
        for idx, sordo in enumerate(sordos[:5]):
            texto = sordo.direccion + '\n' + sordo.detalles_direccion
            if sordo.mejorVisitar:
                mejor_visitar_texto = f"\nMejor Visitar: {sordo.mejorVisitar}" if sordo.mejorVisitar else ""
                texto = texto + mejor_visitar_texto
            gps = f"{sordo.gps_latitud},{sordo.gps_longitud}"
            datos.append((texto, gps, sordo.codigo))

        texto1, gps1, id_sordo1 = datos[0] if len(datos) >= 1 else ('', '', '')
        texto2, gps2, id_sordo2 = datos[1] if len(datos) >= 2 else ('', '', '')
        texto3, gps3, id_sordo3 = datos[2] if len(datos) >= 3 else ('', '', '')
        texto4, gps4, id_sordo4 = datos[3] if len(datos) >= 4 else ('', '', '')
        texto5, gps5, id_sordo5 = datos[4] if len(datos) >= 5 else ('', '', '')

    # Obtener Path Completo de los archivos para qur funcione correctamente el script de generacion
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

    # Llenar y Enviar Path del Archivo de Territorio
    if metodo_entrega =='digital_publicador' or metodo_entrega == 'digital_asignador':
        pdf_bytes, filename = llenarTerritorioDigital(texto1, texto2, texto3, texto4, texto5, territorio_nombre, gps1, gps2, gps3, gps4, gps5, id_sordo1, id_sordo2, id_sordo3, id_sordo4, id_sordo5, id_asignacion, template, boton1, boton2, boton_reportar, boton_entregar)        
    elif metodo_entrega == 'impreso_asignador':
        pdf_bytes, filename = llenarTerritorioImpreso(texto1, texto2, texto3, texto4, texto5, territorio_nombre, gps1, gps2, gps3, gps4, gps5, id_sordo1, id_sordo2, id_sordo3, id_sordo4, id_sordo5, template_impreso)

    return pdf_bytes, filename


def calcular_edad(anio_nacimiento):
    if anio_nacimiento is None:
        return '¿?'
    else:
        return datetime.date.today().year - anio_nacimiento


def enviar_territorio_telegram(chat_id, file_path, territorio):
    try:
        files = {'document': open(f'{file_path}', 'rb')}
        resp = requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendDocument?chat_id={chat_id}", files=files)

        message = f"¡Hola! Se te ha asignado el territorio *{territorio}*. \n Por favor visita las direcciones, predica a cualquier persona que salga e intenta empezar estudios. Anota si no encuentras a nadie y regresa en diferentes horarios. Puedes avisarnos si cualquier detalle es incorrecto. \n ¡Muchas gracias por tu trabajo! 🎒🤟🏼"
        url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage?chat_id={chat_id}&text={message}"
        resp = requests.get(url).json()

        # Cleanup
        os.remove(file_path)
        return True

    except Exception as e:
        print(e)
        return False
    
def enviar_mensaje_telegram(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage?chat_id={chat_id}&text={message}"
        resp = requests.get(url).json()
        return True
    
    except Exception as e:
        print(e)
        return False
    
def borrar_despues_de_segundos(file_path, tiempo):
    time.sleep(tiempo)
    if os.path.exists(file_path):
        os.remove(file_path)


    
# Views de Django

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
                (Q(congregacion=congregacion) & ~Q(asignaciones_de_este_territorio__fecha_fin__isnull=True))
                |(Q(congregacion=congregacion) & Q(asignaciones_de_este_territorio__isnull=True))
                ).annotate(count=Count('asignaciones_de_este_territorio')).order_by('numero')

        messages = get_messages(request)
        for message in messages:
            print(message)

        return render(request, "webTerritorios/asignar.html", {
            "publicadores": publicadores,
            "territorios": territorios,
        })
    
    def post(self, request):

        territorio = request.POST.get('territorio')
        publicador = request.POST.get('publicador')
        asignador = request.user.publicador.nombre

        # DIGITAL TELEGRAM
        if request.POST.get('enviarTelegram'):

            file_path = preparar_y_generar_territorio(publicador, territorio, 'digital_publicador', solo_pdf=False)
            # Notificar Administrador
            enviar_mensaje_telegram(os.environ['TELEGRAM_ADMIN_CHAT_ID'], f'ℹ️ El territorio {territorio_nombre} ha sido asignado a {publicador.nombre} por {asignador} correctamente. Se ha enviado al Telegram del publicador')
            
            # Variables para enviar a Telegram
            chat_id = Publicador.objects.get(pk=publicador).telegram_chatid
            territorio = Territorio.objects.get(pk=territorio)
            territorio_nombre = str(territorio.numero) + ' - ' + territorio.nombre
            publicador = Publicador.objects.get(pk=publicador)
            
            if enviar_territorio_telegram(chat_id, file_path, territorio_nombre):
                messages.success(request, f'Territorio {territorio_nombre} enviado a Telegram de {publicador.nombre} correctamente')
                
                return redirect(reverse("webTerritorios:asignar"))
            else:
                messages.error(request, 'Error al enviar territorio a Telegram')
                return redirect(reverse("webTerritorios:asignar"))

        # DIGITAL DESCARGAR NAVEGADOR
        elif request.POST.get('registrarPDFdigital'):
            file_path = preparar_y_generar_territorio(publicador, territorio, 'digital_publicador', solo_pdf=False)

            # Notificar Administrador
            territorio = Territorio.objects.get(pk=territorio)
            territorio_nombre = str(territorio.numero) + ' - ' + territorio.nombre
            publicador = Publicador.objects.get(pk=publicador)
            publicador_nombre = publicador.nombre
            enviar_mensaje_telegram(os.environ['TELEGRAM_ADMIN_CHAT_ID'], f'ℹ️ El territorio {territorio_nombre} ha sido asignado a {publicador_nombre} por {asignador} correctamente. Se ha descargado el territorio digitalmente')
            
            # Delayed Cleanup
            thread_borrar = threading.Thread(target=borrar_despues_de_segundos, args=(file_path, 30))
            thread_borrar.start()

            return FileResponse(open(file_path, 'rb'), as_attachment=True)

        # IMPRESO DESCARGAR
        elif request.POST.get('registrarPDFimprimir'):
            
            file_path = preparar_y_generar_territorio(publicador, territorio, 'impreso_asignador', solo_pdf=False)
            
            # Notificar Administrador
            territorio = Territorio.objects.get(pk=territorio)
            territorio_nombre = str(territorio.numero) + ' - ' + territorio.nombre
            publicador = Publicador.objects.get(pk=publicador)
            publicador_nombre = publicador.nombre
            enviar_mensaje_telegram(os.environ['TELEGRAM_ADMIN_CHAT_ID'], f'ℹ️ El territorio {territorio_nombre} ha sido asignado a {publicador_nombre} por {asignador} correctamente. Se ha descargado el territorio para imprimir')
            
            # Delayed Cleanup
            thread_borrar = threading.Thread(target=borrar_despues_de_segundos, args=(file_path, 30))
            thread_borrar.start()

            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        

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
                ( (Q(congregacion=congregacion_id) & ~Q(asignaciones_de_este_territorio__fecha_fin__isnull=True))
                |(Q(congregacion=congregacion_id) & Q(asignaciones_de_este_territorio__isnull=True)) )
                & Q(activo=True)
                ).annotate(count=Count('asignaciones_de_este_territorio')).order_by('numero')
            serializer = TerritorioSerializer(queryset, many=True)
            return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def congregacion(self, request):
        data = request.data
        congregacion_id = data.get('congregacion_id')
        if congregacion_id is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Territorio.objects.filter(congregacion=congregacion_id)
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
            serializer = PublicadorExtendidoSerializer(queryset, many=True)
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
        
    # Obtener el publicador con usergroup 'superadmin' de la congregacion del publcador que solicita
    @action(detail=False, methods=['post'])
    def superadmin_congregacion(self, request):
        data = request.data
        id_publicador = data.get('publicador_id')
        publicador = Publicador.objects.get(pk=id_publicador)
        queryset = Publicador.objects.filter(user__groups__name='superadministradores', congregacion=publicador.congregacion)
        serializer = PublicadorSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # Obtener todos los usuarios con el grupo superadmin
    @action(detail=False, methods=['get'])
    def superadmin(self, request):
        queryset = Publicador.objects.filter(user__groups__name='superadministradores')
        serializer = PublicadorSerializer(queryset, many=True)
        return Response(serializer.data)

class SordoViewSet(viewsets.ModelViewSet):
    queryset = Sordo.objects.all()
    serializer_class = SordoSerializer

    @action(detail=False, methods=['post'])
    def para_kml_y_gpx(self, request):
        data = request.data
        id_congregacion = data.get('congregacion_id')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Sordo.objects.filter(Q(congregacion=id_congregacion) & Q(estado_sordo__nombre='Habilitado') ).order_by('territorio__numero', 'territorio__nombre', 'codigo')
            serializer = SordoSerializer(queryset, many=True)
            return Response(serializer.data)

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
            ).order_by('fecha_asignacion')
            serializer = AsignacionSerializer(queryset, many=True)
            return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def entregadas(self, request):
        data = request.data
        id_congregacion = data.get('congregacion_id')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Asignacion.objects.filter(
                Q(territorio__congregacion=id_congregacion) & 
                Q(fecha_fin__isnull=False)
            ).order_by('-fecha_fin')[:15] # Ultimas 15 entregas
            serializer = AsignacionSerializer(queryset, many=True)
            return Response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def reporte_congregacion(self, request):
        data = request.data
        id_congregacion = data.get('congregacion_id')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Asignacion.objects.filter(
                Q(territorio__congregacion=id_congregacion) 
            )
            serializer = AsignacionSerializer(queryset, many=True)
            return Response(serializer.data)

@csrf_exempt
def asignar_territorio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            publicador_id = data.get('publicador_id')
            territorio_id = data.get('territorio_id')
            metodo_entrega = data.get('metodo_entrega')
            solo_pdf = data.get('solo_pdf')
            
            pdf_bytes, filename = preparar_y_generar_territorio(publicador_id, territorio_id, metodo_entrega, solo_pdf)

            chat_id = Publicador.objects.get(pk=publicador_id).telegram_chatid
            territorio = Territorio.objects.get(pk=territorio_id)
            territorio_nombre = str(territorio.numero) + ' - ' + territorio.nombre

            # Codificar los bytes a base64 para enviarlos por JSON
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

            # Enviar contenido en lugar de path
            if metodo_entrega =='digital_publicador' or metodo_entrega == 'digital_asignador':
                return JsonResponse({
                    'chat_id': chat_id, 
                    'pdf_data': pdf_base64, 
                    'filename': filename,
                    'territorio': territorio_nombre
                }, status=200)
                
            elif metodo_entrega == 'impreso_asignador':
                return JsonResponse({
                    'pdf_data': pdf_base64, 
                    'filename': filename,
                    'territorio': territorio_nombre
                }, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

