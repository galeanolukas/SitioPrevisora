# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import models
from django import forms
from PaginaWeb.settings import DATE_INPUT_FORMATS
# Create your models here.

def subir_media(instance, filename):
	return "galeria/clinicas/" + filename
	
def subir_file(instance, filename):
	return "archivos/clinicas/" + filename


class Contenido(models.Model):
        opciones = (('Principal', 'Principal'),
                    ('Lateral', 'Lateral'),
                    ('Servicios', 'Servicios'),
                    ('Tienda', 'Tienda'),
                    ('Info', 'Info')
                    )
        titulo = models.CharField(max_length=80, null=True, blank=True)
        valor = models.IntegerField(null=True, blank=True)
        categoria = models.CharField(max_length=30, choices=opciones)
        texto = models.TextField()
        imagen = models.FileField(upload_to=subir_file, null=True, blank=True)
        fecha_post = models.DateTimeField(null=True, blank=True)
        
        def __str__(self):
                return str([self.titulo, self.categoria])   

class Especialista(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    matricula = models.IntegerField()
    foto = models.FileField(upload_to=subir_media, null=True, blank=True)
    consultorio = models.ForeignKey('clinicas.Consultorio', on_delete=models.CASCADE, null=True)
    secretaria = models.ForeignKey('clinicas.Agenda', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(['%s %s' % (self.nombre, self.apellido), self.matricula])

class Dia(models.Model):
    DAYS_OF_WEEK = (
            (0, 'Lunes'),
            (1, 'Martes'),
            (2, 'Miercoles'),
            (3, 'Jueves'),
            (4, 'Viernes'),
            (5, 'Sabado'),
            (6, 'Domingo'),
    )    
    dia = models.CharField(max_length=8, choices=DAYS_OF_WEEK)


    def __str__(self):
            return str(self.dia)

class Turno(models.Model):
        consultorio = models.ForeignKey('clinicas.Consultorio', on_delete=models.CASCADE, null=True)
        usuario = models.CharField(max_length=30)
        fecha_hora = models.DateTimeField()
        clave = models.CharField(max_length=5)
        activo = models.BooleanField() 

        def __str__(self):
                return str([self.consultorio, self.fecha_hora])
           

class Agenda(models.Model):
        profesional = models.ForeignKey('clinicas.Especialista', on_delete=models.CASCADE, null=True)
        horario_inicio = models.TimeField()
        horario_final = models.TimeField()
        dias = models.ManyToManyField(Dia)
        turnos = models.ManyToManyField(Turno)

        def __str__(self):
                return str([self.profesional])


class Paciente(models.Model):
        nombre = models.CharField(max_length=100)
        dni = models.IntegerField()
        fecha_nac = models.DateField()
        edad = models.IntegerField()
        correo = models.EmailField()
        direccion = models.CharField(max_length=50)
        telefono = models.IntegerField()
        turnos = models.ManyToManyField(Turno, blank=True)

        def __str__(self):
                return str([self.nombre, self.dni])

class Consulta(models.Model):
        motivo = models.CharField(max_length=100)
        especialista = models.ForeignKey('clinicas.Especialista', on_delete=models.CASCADE)
        fecha_hora = models.DateTimeField()
        observacion = models.TextField(blank=True, null=True)
        adjunto = models.FileField(upload_to=subir_file, null=True, blank=True)

        def __str__(self):
                return str([self.fecha_hora, self.motivo])
                
        
class Ficha(models.Model):
        paciente = models.ForeignKey('clinicas.Paciente', on_delete=models.CASCADE, null=True)
        fecha = models.DateField()
        consultas = models.ManyToManyField(Consulta, blank=True)
        clave = models.CharField(max_length=6)

        def __str__(self):
                return str([self.paciente, self.fecha])
        

class Consultorio(models.Model):
    opciones = (('Nutricion', 'Nutricion'),
                    ('Medico General', 'Medico General'),
                    ('Pediatria', 'Pediatria'),
                    ('Psicologia', 'Psicologia'),
                    ('Odontologia', 'Odontologia')
                )
    nombre = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=30, choices=opciones)
    ubicacion = models.CharField(max_length=200)
    telefono = models.IntegerField()
    email = models.EmailField()
    descripcion = models.TextField(null=True, blank=True)
    precio_consulta = models.IntegerField()
    imagen = models.FileField(upload_to=subir_media, null=True, blank=True)
    fichero = models.ManyToManyField(Ficha, blank=True)

    def __str__(self):
        return str([self.nombre, self.especialidad])


        
    
    
    
