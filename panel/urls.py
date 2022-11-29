from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.home, name="panel_dash"),
    path('notificaciones/', views.mostrar_notif, name='ver_notif'),
    path('mensajes/', views.mostrar_msj, name='msj_interno'),
    path('mensajes/<int:ID>/', views.mostrar_msj, name='msj_interno'),
    path('mail/', views.ver_mensajes, name='ver_msj'),
    path('mail/responder/<str:tp>/<int:ID>/', views.notificar_x_mail, name='enviar_mail'),
    path('registros/<str:tp>/', views.consulta_x_registros, name='ver_r'),
    path('registros/editar/<str:tp>/<int:ID>/', views.editar_registro, name='editar_r'),
    path('registros/eliminar/<str:tp>/<int:ID>/', views.eliminar_registro, name='eliminar_r'),
    path('contenidos/<str:tp>/<int:ID>/', views.crea_edita_contenido, name='contenidos'),
    path('tienda/<str:tp>/', views.gestion_tienda, name='tienda'),
    path('tienda/<str:tp>/<int:ID>/', views.gestion_tienda, name='tienda'),
    ] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
