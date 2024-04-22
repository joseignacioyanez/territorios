
import datetime
import json
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
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response


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
@csrf_exempt
def datos_usuario_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not user_id:
            return JsonResponse({'error': 'user_id not provided'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        user_data = {
            'id': user.id,
            'username': user.username,
            'nombre': user.publicador.nombre,
            'groups': list(user.groups.values_list('name', flat=True)),
            'telegram_chatid': user.publicador.telegram_chatid,
            'congregacion_nombre': user.publicador.congregacion.nombre,
            'congregacion_id': user.publicador.congregacion.id,
        }

        return JsonResponse(user_data)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def publicadores_activos_misma_congregacion_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not user_id:
            return JsonResponse({'error': 'user_id not provided'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        congregacion_id = user.publicador.congregacion.id
        filtered_users = User.objects.filter(publicador__congregacion__id=congregacion_id, publicador__activo=True)

        user_list = []
        for user in filtered_users:
            user_data = {
                'id': user.id,
                'username': user.username,
                "nombre": user.publicador.nombre,
                'groups': list(user.groups.values_list('name', flat=True)),
                'chat_id': user.publicador.telegram_chatid,  
                'congregacion_nombre': user.publicador.congregacion.nombre,
                'congregacion_id': user.publicador.congregacion.id,
            }
            user_list.append(user_data)

        return JsonResponse(user_list, safe=False)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_usuario_por_chatid_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_chatid = data.get('telegram_chatid')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not telegram_chatid:
            return JsonResponse({'error': 'telegram_chatid not provided'}, status=400)

        try:
            user = User.objects.get(publicador__telegram_chatid=telegram_chatid)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        return JsonResponse({'user_id': user.id})

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

        
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
        id_congregacion = data.get('id_congregacion')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Territorio.objects.filter(
                Q(congregacion=id_congregacion) & 
                Q(asignaciones_de_este_territorio__fecha_fin__isnull=False) | Q(asignaciones_de_este_territorio__isnull=True)
            )
            serializer = TerritorioSerializer(queryset, many=True)
            return Response(serializer.data)

class PublicadorViewSet(viewsets.ModelViewSet):
    queryset = Publicador.objects.all()
    serializer_class = PublicadorSerializer

class SordoViewSet(viewsets.ModelViewSet):
    queryset = Sordo.objects.all()
    serializer_class = SordoSerializer

class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all()
    serializer_class = AsignacionSerializer

    @action(detail=False, methods=['post'])
    def pendientes(self, request):
        data = request.data
        id_congregacion = data.get('id_congregacion')
        if id_congregacion is None:
            return Response({'error': 'No se proporcionó el ID de la congregación en la solicitud'}, status=400)
        else:
            queryset = Asignacion.objects.filter(
                Q(territorio__congregacion=id_congregacion) & 
                Q(fecha_fin__isnull=True)
            )
            serializer = AsignacionSerializer(queryset, many=True)
            return Response(serializer.data)
