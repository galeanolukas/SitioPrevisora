# -*- coding: utf-8 -*-
# encoding: latin1
from __future__ import unicode_literals
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db import models
from django import forms
from PaginaWeb.settings import DATE_INPUT_FORMATS #, AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
##from djrichtextfield.models import RichTextField
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import datetime

# Create your models here.
grupo_previsora, created = Group.objects.get_or_create(name='Previsora')
grupo_previsora, created = Group.objects.get_or_create(name='Ordenes')
grupo_cocheria, created = Group.objects.get_or_create(name='Cocheria')
grupo_clinicas, created = Group.objects.get_or_create(name='Clinicas')

def subir_media(instance, filename):
	return "galeria/sitio/" + filename
	
def subir_file(instance, filename):
	return "archivos/sitio/" + filename

def subir_recibo(instance, filename):
        return "archivos/comprobantes/" + filename

def subir_doc(instance, filename):
	return "archivos/doc/" + filename

def subir_plantilla(instance, filename):
	return "archivos/sitio/doc/xlsx/" + filename

class Plan(models.Model):
        titulo = models.CharField(max_length=10)
        periodo = models.CharField(max_length=10)
        vigencia = models.IntegerField()
        valor = models.IntegerField()
        descuento = models.IntegerField()
        descuento_grupo = models.IntegerField(null=True, blank=True)
        servicio = models.CharField(max_length=10)
        total = models.IntegerField()
        descrip = models.TextField(null=True, blank=True)
        
        class Meta:
                verbose_name = 'Plan'
                verbose_name_plural = 'Planes'

        def __str__(self):
                return str("%s: %s" % (self.titulo, self.periodo))

class PerfilUsuario(models.Model):
        usuario = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='user', null=True, blank=True)
        telefono = models.CharField(max_length=20, blank=True, default='')
        nombre = models.CharField(max_length=100, blank=True, default='')
        ciudad = models.CharField(max_length=100, default='Formosa, Formosa', blank=True)
        num_afiliado = models.IntegerField(blank=True, null=True)

        class Meta:
                verbose_name = 'Perfil'
                verbose_name_plural = 'Perfiles de Registrados'

        def __str__(self):
                txt = "{0} : {1}"
                return txt.format(self.usuario, self.nombre)

def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = PerfilUsuario(usuario=user)
        user_profile.save()
        
post_save.connect(create_profile, sender='auth.User')

class Contacto(models.Model):
        nombre = models.CharField(max_length=200)
        email = models.EmailField(max_length=40, blank=True)
        numero = models.CharField(max_length=20, null=True)
        fecha = models.DateTimeField(auto_now_add=True, null=True, blank=True)
        texto = models.TextField()

        class Meta:
                verbose_name = 'Mensaje'
                verbose_name_plural = 'Mensajes de Contactos'


        def __str__(self):
                return str([self.nombre, self.fecha])
        

class Solicitud(models.Model):
        usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name="solicitante")
        nombre = models.CharField(max_length=30)
        apellido = models.CharField(max_length=30)
        direccion = models.CharField(max_length=100)
        dni = models.CharField(max_length=9)
        telefono = models.CharField(max_length=11)
        correo = models.EmailField(max_length=40, blank=True, null=True)
        validacion = models.CharField(max_length=5, null=True, blank=True)
        fecha_nac = models.DateField(null=True, blank=True)
        fecha = models.DateField(auto_now_add=True, null=True, blank=True)
        verificado = models.BooleanField(default=False)
        aprobada = models.BooleanField(default=False)
        plan = models.ForeignKey('sitio.Plan', on_delete=models.CASCADE, null=True, related_name="plan_asignado")
        
        class Meta:
                verbose_name = 'Solicitud'
                verbose_name_plural = 'Solicitudes de Afiliacion'


        def __str__(self):
                txt = "Solicitud de {0} {1}: {2}"
                return txt.format(self.apellido, self.nombre, self.fecha.strftime("%d/%m/%Y"))

class Cupones(models.Model):
        usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name="gestor", blank=True)
        nombre = models.CharField(max_length=30, null=True, blank=True)
        correo = models.EmailField(max_length=40, blank=True, null=True)
        telefono = models.CharField(max_length=13)
        numero_afiliado = models.IntegerField()
        fecha = models.DateTimeField(default=timezone.now, null=True, blank=True)
        numero_cupon = models.IntegerField(validators=[MinValueValidator(1500), MaxValueValidator(5000)], null=True)
        comprobante = models.FileField(upload_to=subir_doc, null=True, blank=True)
        verificado = models.BooleanField(default=False)

        class Meta:
                verbose_name = 'Cupon'
                verbose_name_plural = 'Cupones Del Sorteo'


        def __str__(self):
                return str(["%s %s" % (self.nombre, self.numero_afiliado), self.fecha.strftime("%d/%m/%Y-%h%m%s")])
        
                
class Cliente(models.Model):
        usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name="usuarios")
        numero = models.IntegerField(null=True, blank=True)
        fecha = models.DateField(default=timezone.now)
        activo = models.BooleanField(default=False)
        monto = models.IntegerField(null=True, blank=True)
        datos = models.ForeignKey('sitio.Solicitud', on_delete=models.CASCADE, related_name="Solicitudes")


        class Meta:
                verbose_name = 'Afiliado'
                verbose_name_plural = 'Afiliados'
                
        def __str__(self):
                txt = "{}, {}, {}, {}"
                return txt.format(self.datos.apellido, self.datos.nombre, self.fecha.strftime("%d/%m/%Y"), self.numero)


class MercadoPagoData(models.Model):
        nombre = models.CharField(max_length=50)
        public_key = models.CharField(max_length=200)
        access_token = models.CharField(max_length=200)
##        client_id = models.IntegerField(null=True, blank=False)
        client_secret = models.CharField(max_length=100, null=True, blank=False)

        class Meta:
                verbose_name = 'Cuenta de cobro'
                verbose_name_plural = 'Cuentas MercadoPago'

        def __str__(self):
                return ("%s" % self.nombre)

class MediosDePagos(models.Model):
        nombre = models.CharField(null=True, blank=True, max_length=120)
        codigo = models.CharField(null=True, blank=True, max_length=5)

        class Meta:
                verbose_name = 'Forma de Pago'
                verbose_name_plural = 'Medios de Pagos'

        def __str__(self):
                return self.nombre
        
        
class Pago(models.Model):
        CHOICES = (
        ('MercadoPago', 'MercadoPago'),
        ('CBU', 'CBU'),)
        medio = models.ForeignKey('MediosDePagos', on_delete=models.CASCADE, null=True, related_name="forma_pago")
##        medio = models.CharField(max_length=50, choices=CHOICES)
        valor = models.IntegerField()
        recibo_n = models.IntegerField()
##        cliente = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="cliente")
        comprobante = models.FileField(upload_to=subir_file, null=True, blank=True)
        fecha = models.DateTimeField(default=timezone.now)
        
        class Meta:
                verbose_name = 'Pago'
                verbose_name_plural = 'Pagos Realizados'

        def __str__(self):
                return str([self.recibo_n, self.fecha])

class CuentaDeClientes(models.Model):
        nombre = models.CharField(null=True, blank=True, max_length=120)
        num_afiliado = models.IntegerField()
        fecha = models.DateTimeField()
        ingresos = models.IntegerField()
        egresos = models.IntegerField()
        pagos = models.ManyToManyField(Pago, blank=True)

        class Meta:
                verbose_name = 'CC'
                verbose_name_plural = 'CC De Usuarios'

        def __str__(self):
                return self.nombre + '' + str(self.num_afiliado)

class AfiliadosDeSorteo(models.Model):
        titulo = models.CharField(max_length=100, blank=True)
        archivo = models.FileField(upload_to=subir_plantilla)
        fecha = models.DateField(default=timezone.now)
        activo = models.BooleanField(default=True)

        class Meta:
                verbose_name = 'Planilla'
                verbose_name_plural = 'Planillas de Sorteo'
                

        def __str__(self):
                return str([self.titulo, self.fecha])

class PremiosDeSorteo(models.Model):
        nombre = models.CharField(max_length=200)
        orden = models.IntegerField()
        imagen = models.ImageField(upload_to=subir_media, null=True, blank=True)

        class Meta:
                verbose_name = 'Premio'
                verbose_name_plural = 'Premios del sorteo'

        def __str__(self):
                return str([self.nombre, self.orden])
        
class RecibosDePagos(models.Model):

        CHOICES = (
        ('Enero', 'Enero'),
        ('Febrero', 'Febrero'),
        ('Marzo', 'Marzo'),
        ('Abril', 'Abril'),
        ('Mayo', 'Mayo'),
        ('Junio', 'Junio'),
        ('Julio', 'Julio'),
        ('Agosto', 'Agosto'),
        ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'),
        ('Noviembre', 'Noviembre'),
        ('Diciembre', 'Diciembre'),)
        
        YEAR_CHOICES = [(r,r) for r in range(1984, datetime.date.today().year+1)]
        
        nombre = models.CharField(max_length=50, blank=True, null=True)
        mes = models.CharField(max_length=50, choices=CHOICES)
        ano = models.IntegerField(choices=YEAR_CHOICES, default=timezone.now().year)
        fecha = models.DateField(default=timezone.now)
        archivo = models.FileField(upload_to=subir_plantilla)
        activo = models.BooleanField(default=True)
        
        class Meta:
                verbose_name = 'Plantilla'
                verbose_name_plural = 'Plantillas de Recibos'


    
        def __str__(self):
                return str([self.nombre, self.mes, self.ano])
        
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
        texto = RichTextUploadingField()
        imagen = models.FileField(upload_to=subir_media, null=True, blank=True)
        mostrar_img = models.BooleanField(default=True)
        fecha_post = models.DateTimeField(null=True, blank=True)
        
        def __str__(self):
                return str([self.titulo, self.categoria])

                
class Aviso(models.Model):
        titulo = models.CharField(max_length=30)
        entrada = models.TextField()
        fecha = models.DateTimeField(default=timezone.now, null=True, blank=True)
        
        def __str__(self):
                return str([self.titulo, self.fecha])

class Notificaciones(models.Model):
        opciones = (
                    ("contacto", 'Contactos'),
                    ("pago", 'Pago'),
                    ("usuario", 'Usuario'),
                    ("tienda", 'Tienda'),
                    ("solicitud", 'Solicitud')
                    )
        seccion = models.CharField(max_length=100, choices=opciones)
        activa = models.BooleanField(default=True)
        titulo = models.CharField(max_length=300)
        mensaje = models.TextField()
        fecha = models.DateTimeField(auto_now_add=True,)

        class Meta:
                verbose_name = 'Notificacion'
                verbose_name_plural = 'Notificaciones'


        def __str__(self):
                txt = "{0}: {1}"
                return txt.format(self.titulo, self.fecha.strftime("%d/%m/%Y-%H:%I"))

class Media(models.Model):
        nombre = models.CharField(max_length=30)
        titulo = models.CharField(max_length=30, null=True, blank=True)
        archivo = models.FileField(upload_to=subir_media, null=True, blank=True)

        class Meta:
                verbose_name = 'AudioVideo'
                verbose_name_plural = 'Archivos Multimedia'


    
        def __str__(self):
                return self.nombre

##NOTIFICACIONES=======================================================================
		
### Notificacion de contactos     
@receiver(post_save, sender=Contacto)
def notif_contacto(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "contacto"
        nueva_notif.titulo = "Nuevo mensaje de contacto de %s" % instance.nombre
        nueva_notif.mensaje = '''<h2>%s</h2>
                                <p><strong>Email:</strong> %s</p>
                                <p><strong>Telefono:</strong> %s</p>
                                <p><strong>Fecha:</strong> %s</p>
                                <span>%s</span>''' % (instance.nombre, instance.email, instance.numero, timezone.now, instance.texto)
        nueva_notif.save()
    
### Notificacion de registros       
@receiver(post_save, sender=PerfilUsuario)
def notif_registro(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "registro"
        nueva_notif.titulo = "Nuevo usuario registrado: %s" % instance.usuario
        nueva_notif.mensaje = '''<h2>NUEVO REGISTRO DE:</h2><p><strong>Nombre y apellido:</strong> %s</p><p><strong>Email:</strong> %s</p>
                                        <p>Fecha de registro: %s</p>
                              ''' % (instance.usuario, instance.nombre, timezone.now)
        nueva_notif.save()

### Notificacion de solicitud       
@receiver(post_save, sender=Solicitud)
def notif_solicitud(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "solicitud"
        nueva_notif.titulo = "Nueva solicitud cargada: %s" % instance.nombre
        nueva_notif.mensaje = '''<h2>Solicitud de %s %s</h2>
                                <p>DNI: %s</p>
                                <p>Telefono: %s</p>
                                <p>Email: %s</p>''' % (instance.apellido, instance.nombre, instance.dni, instance.telefono, instance.correo)
        nueva_notif.save()

### Notificacion de Pagos       
@receiver(post_save, sender=Pago)
def notif_pagos(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "pago"
        nueva_notif.titulo = "Nuevo pago registrado: %s" % instance.recibo_n
        nueva_notif.mensaje = '''<h2>%s</h2>
                                 <p><h3>$ %s</h3></p>
                                 <p><strong>Cliente N°:</strong> %s</p>
                                 <p><strong>Fecha:</strong> %s</p>''' % (instance.medio, instance.valor, instance.recibo_n, instance.fecha)
        nueva_notif.save()
