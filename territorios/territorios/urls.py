"""territorios URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from webTerritorios.views import TerritoriosLoginView, logoutView
from rest_framework import routers
from webTerritorios import views as webTerritorios_views

from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView


# Router para la API
router = routers.DefaultRouter()
router.register(r'congregaciones', webTerritorios_views.CongregacionViewSet, basename="congregaciones")
router.register(r'publicadores', webTerritorios_views.PublicadorViewSet, basename="publicadores")
router.register(r'sordos', webTerritorios_views.SordoViewSet, basename="sordos")
router.register(r'territorios', webTerritorios_views.TerritorioViewSet, basename="territorios")
router.register(r'estados', webTerritorios_views.EstadoSordoViewSet, basename="estados")
router.register(r'asignaciones', webTerritorios_views.AsignacionViewSet, basename="asignaciones")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', TerritoriosLoginView.as_view(template_name="registration/login.html"), name="login"),
    path('logout/', logoutView, name='logout'),
    path('api/', include(router.urls)),
    path("webTerritorios/", include("webTerritorios.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
