# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

class PerfilInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de usuario'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)

 
class PlanesAdmin(admin.ModelAdmin):
    list_display = ['periodo', 'vigencia', 'valor', 'cuotas',
                    'descuento', 'descuento_grupo', 'servicio', 'total',
                    'descrip']
##    list_filter = ['descrip', 'vigencia', 'servicio']
    list_editable = ['valor', 'descuento', 'descuento_grupo', 'total']
##
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(Plan, PlanesAdmin)
admin.site.register(Cliente)
admin.site.register(Solicitud)
admin.site.register(Aviso)
admin.site.register(Pago)
admin.site.register(Contenido)
admin.site.register(User, PerfilUsuario)
admin.site.register(Cupones)
admin.site.register(Media)
admin.site.register(Contacto)
admin.site.register(Notificaciones)
admin.site.register(MercadoPagoData)
admin.site.register(AfiliadosDeSorteo)
admin.site.register(PremiosDeSorteo)
admin.site.register(MediosDePagos)
admin.site.register(CategoriaDeServicio)
admin.site.register(ConsultaxAfiliado)
admin.site.register(Sistema)
