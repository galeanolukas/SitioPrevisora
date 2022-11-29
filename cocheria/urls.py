from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static, serve
from . import views

app_name = 'cocheria'

urlpatterns = [
    path('', views.home, name="home"),
    path('administrador/', admin.site.urls),
    path('salir/', views.cerrar_sesion, name="salir"),
    path('panel/', views.ver_panel, name="panel"),
    path('contacto/', views.vista_contacto, name="contacto"),
    path('servicios/', views.servicios, name="servicios"),
    path('homenajes/', views.homenajes, name="homenajes"),
    path('homenajes/nuevo/', views.crear_obituario, name="obituario"),
    path('homenajes/editar/<ID>/', views.editar_obituario, name="editar_obi"),
    path('homenajes/eliminar/<ID>/', views.borrar_obi, name="eliminar_obi"),
    path('contenido/nuevo/', views.nuevo_contenido, name="nuevo"),
    path('contenido/ver/', views.mostrar_contenido, name="mostrar"),
    path('contenido/editar/<ID>/', views.editar_contenido, name="editar"),
    path('contenido/eliminar/<ID>/', views.borrar_contenido, name="eliminar"),
    ]
