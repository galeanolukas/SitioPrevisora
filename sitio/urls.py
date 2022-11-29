"""Sitio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static, serve
from . import views

urlpatterns = [
    ##url(r'^home/', views.home_en_construccion, name="home2"),
    path('', views.home, name="home"),
    #path('login/', views.login_vista, name='login'),
    path('accounts/login/', views.login_vista, name='login'),
    path('salir/', views.cerrar_sesion, name='salir'),
    path('contacto/', views.vista_contacto, name="contacto"),
    path('contenido/ver/', views.mostrar_contenido, name="ver"),
    path('contenido/nuevo/', views.nuevo_contenido, name="nuevo"),
    path('contenido/editar/<ID>/', views.editar_contenido, name="editar"),
    path('contenido/eliminar/<ID>/', views.borrar_contenido, name="eliminar"),
    path('admin/panel/', views.panel_admin, name="panel"),
    path('admin/consultar/', views.buscar, name="buscar"),
    path('admin/sorteo/api/', views.sorteo_api, name="sorteo_api"),
    path('admin/contactos/', views.ver_mensajes, name="ver_mensajes"),
    path('admin/solicitudes/', views.ver_afiliado, name="buscar_afiliado"),
    path('admin/cupones/', views.consulta_cupones, name="buscar_cupones"),
    path('admin/cupones/planilla/', views.descargar_csv, name="descarga_csv"),
    path('admin/solicitudes/alta/<ID>/', views.dar_alta, name="alta"),
    path('admin/notificaciones/ver/<ID>/', views.mostrar_notif, name="ver_notif"),
    path('admin/solicitudes/baja/<ID>/', views.dar_baja, name="baja"),
    path('admin/consultar/eliminar/<ID>/', views.eliminar_usuario, name="elimina_usuario"),
    path('admin/avisos/<ID>/', views.enviar_aviso, name="aviso"),
    path('clientes/panel/', views.panel_cliente, name="clientes"),
    path('clientes/registro/', views.vista_registro, name="registro"),
    path('clientes/solicitud/', views.vista_solicitud, name="afiliacion"),
    path('clientes/solicitud/pago/<ID>/', views.cobrar_solicitud, name="pago_solicitud"),
    path('clientes/validar/', views.validar, name="validar"),
    path('clientes/consulta/', views.consulta_x_dni, name="consulta"),
    path('clientes/sorteo/', views.registro_al_sorteo, name="sorteo"),
    path('clientes/sorteo/cupon/', views.cupon_sorteo, name="cupon_sorteo"),
    path('clientes/asociar/<ID>/', views.asociar_a_usuario, name="asociar"),
    path('clientes/planes/', views.ver_planes, name="planes"),
    path('clientes/calcular/', views.calcular_plan, name="calcular"),
    path('clientes/recuperar/', views.recuperar_pass, name="recuperar"),
    path('clientes/pagos/', views.pagos_online, name="pagos"),
    path('clientes/pagos/<str:tp>/', views.pagos_online, name="pagos"),
    path('clientes/pago/<str:estado>/<str:codigo_factura>/', views.regis_pago_online, name="confirmar_pago"),
##    path('clientes/pagos/recibo/<ID>/', views.cuponpago_pdf, name="recibo_pdf"),
    path('admin/editar/<ID>/', views.editar_usuario, name="editar_usuario"),
    path('clientes/editar/<ID>/', views.editar_cliente, name="edita_cli"),
    path('servicios/', views.mostrar_contenido, name="mostrar"),
    path('administrador/', admin.site.urls, name="admin_db"),

]
