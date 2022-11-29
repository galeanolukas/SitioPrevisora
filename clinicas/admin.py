# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Especialista, Consultorio, Contenido, Agenda, Turno, Dia, Paciente
# Register your models here.

admin.site.register(Contenido)
admin.site.register(Agenda)
admin.site.register(Paciente)
admin.site.register(Turno)
admin.site.register(Dia)
admin.site.register(Consultorio)
admin.site.register(Especialista)
