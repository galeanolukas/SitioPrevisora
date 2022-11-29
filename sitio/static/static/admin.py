# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Plan)
admin.site.register(Cliente)
admin.site.register(Solicitud)
admin.site.register(Aviso)
admin.site.register(Pago)
admin.site.register(Contenido)
admin.site.register(PerfilUsuario)
admin.site.register(Cupones)
admin.site.register(RecibosDePagos)
admin.site.register(Media)
admin.site.register(Contacto)
admin.site.register(Notificaciones)
admin.site.register(MercadoPagoData)
admin.site.register(AfiliadosDeSorteo)
admin.site.register(PremiosDeSorteo)
admin.site.register(MediosDePagos)
admin.site.register(CuentaDeClientes)
