from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'clinicas'

urlpatterns = [
    path('', views.home, name="home"),
    path('administrador/', admin.site.urls),
    path('panel/', views.ver_panel, name="panel"),
    path('salir/', views.cerrar_sesion, name="salir"),
    path('contenido/nuevo/', views.nuevo_contenido, name="nuevo"),
    path('contenido/ver/', views.mostrar_contenido, name="mostrar"),
    path('contenido/editar/<ID>/', views.editar_contenido, name="editar"),
    path('contenido/eliminar/<ID>/', views.borrar_contenido, name="eliminar")
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
