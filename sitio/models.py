# -*- coding: utf-8 -*-
# encoding: latin1
from __future__ import unicode_literals
from django.contrib.auth.models import Group
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db import models
from django import forms
from PaginaWeb.settings import DATE_INPUT_FORMATS #, AUTH_USER_MODEL
from django.contrib.auth.models import (AbstractUser, BaseUserManager)
from django.db.models.signals import post_save
from django.contrib.auth.models import User
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
        cuotas = (('0', '1'),
                  ('1', '3'),
                  ('2', '6'),
                  ('3', '9'),
                  ('4', '12'),
                  ('5', '24'),
                  ('6', '30'))
        titulo = models.CharField(max_length=10)
        periodo = models.CharField(max_length=10)
        vigencia = models.IntegerField()
        valor = models.DecimalField(max_digits=10, decimal_places=2)
        descuento = models.IntegerField()
        descuento_grupo = models.IntegerField(null=True, blank=True)
        servicio = models.CharField(max_length=100)
        cuotas = models.CharField(choices=cuotas, max_length=2, default='0')
        total = models.DecimalField(max_digits=10, decimal_places=2)
        descrip = models.TextField(null=True, blank=True)

        class Meta:
                verbose_name = 'Plan'
                verbose_name_plural = 'Planes y Servicios'

        def __str__(self):
                return "%s de %s años" % (self.titulo, self.periodo)

class CategoriaDeServicio(models.Model):
        titulo = models.CharField(max_length=100, blank=True, null=True)
        codigo = models.IntegerField(default=0)

        class Meta:
                verbose_name = "Servicio"
                verbose_name_plural = "Servicios Pagos del Sitio"

        def __str__(self):
                return "%s: %s" % (self.codigo, self.titulo)

class PerfilUsuario(models.Model):
        usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
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

        def fechayhora(self):
                return self.fecha.strftime('%d/%m/%Y %H:%M')


        def __str__(self):
                return str([self.nombre, self.fechayhora()])


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
        verificado = models.BooleanField(verbose_name='Confirmado', default=False)
        aprobada = models.BooleanField(verbose_name='Pagado', default=False)
        plan = models.ForeignKey('sitio.Plan', on_delete=models.CASCADE, null=True, related_name="plan_asignado")

        class Meta:
                verbose_name = 'Solicitud'
                verbose_name_plural = 'Solicitudes de Afiliacion'

        def edad(self):
                hoy = timezone.now().date()
                num = 'No registro nacimiento'
                if self.fecha_nac:
                        num = int(hoy.strftime('%Y')) - int(self.fecha_nac.strftime('%Y'))
                        if int(hoy.strftime('%m')) < int(self.fecha_nac.strftime('%m')):
                                num = num - 1

                return num

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
                return str(["%s %s" % (self.nombre, self.numero_afiliado), self.fecha.strftime("%d/%m/%Y")])

class MercadoPagoData(models.Model):
        nombre = models.CharField(max_length=50)
        public_key = models.CharField(max_length=200)
        access_token = models.CharField(max_length=200)
        client_secret = models.CharField(max_length=100, null=True, blank=False)

        class Meta:
                verbose_name = 'Cuenta de cobro'
                verbose_name_plural = 'Cuentas MercadoPago'

        def __str__(self):
                return ("%s" % self.nombre)

class MediosDePagos(models.Model):
        nombre = models.CharField(null=True, blank=True, max_length=120)
        codigo = models.IntegerField(null=True, blank=True)

        class Meta:
                verbose_name = 'Forma de Pago'
                verbose_name_plural = 'Medios de Pagos'

        def __str__(self):
                return '%s: %s' % (self.codigo, self.nombre)

class Sistema(models.Model):
	nombre = models.CharField(null=True, blank=True, max_length=300)
	enlace = models.URLField(null=True, blank=True)

	class Meta:
		verbose_name = 'Enalces'
		verbose_name_plural = 'Enlaces al Sistema de Gestion'

		def __str__(self):
			return self.nombre

class ConsultaxAfiliado(models.Model):
        titulo = models.ForeignKey('CategoriaDeServicio',verbose_name="Concepto", on_delete=models.CASCADE, related_name="factura", null=True, blank=True)
        numero = models.IntegerField(verbose_name="Numero de Afiliado/Solicitud")
        nombre = models.CharField(null=True, blank=True, max_length=120)
        dni = models.CharField(null=True, blank=True, max_length=11)
        valor = models.DecimalField(verbose_name="monto", null=True, blank=True, max_digits=10, decimal_places=2)
        fecha = models.DateTimeField(default=timezone.now)
        codigo = models.CharField(null=True, blank=True, max_length=8)


        class Meta:
                verbose_name = 'Factura de afiliado/usuario'
                verbose_name_plural = 'Facturacion de usuarios'

        def __str__(self):
                return '%s: [%s, %s]' % (self.titulo, self.nombre, self.fecha.strftime('%d:%m:%Y'))

class Pago(models.Model):
        usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="cliente", null=True, blank=True)
        categoria = models.ForeignKey('ConsultaxAfiliado', verbose_name='factura', on_delete=models.CASCADE, null=True, related_name="factura")
        medio = models.ForeignKey('MediosDePagos', on_delete=models.CASCADE, related_name="medio", null=True, blank=True)
        valor = models.DecimalField(verbose_name="monto", null=True, blank=True, max_digits=10, decimal_places=2)
        recibo_n = models.IntegerField()
        comprobante = models.FileField(upload_to=subir_file, null=True, blank=True)
        notificado = models.BooleanField(default=False)
        fecha = models.DateTimeField(default=timezone.now)

        class Meta:
                verbose_name = 'Pago'
                verbose_name_plural = 'Pagos Registrados'

        def __str__(self):
                return str([self.recibo_n, self.fecha.strftime('%d/%m/%Y'), self.categoria])

class Cliente(models.Model):
        usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, related_name="usuarios")
        numero = models.IntegerField(null=True, blank=True)
        fecha = models.DateField(verbose_name='fecha de afiliacion', default=timezone.now)
        fecha2 = models.DateField(verbose_name='fin de carencia', null=True, blank=True)
        activo = models.BooleanField(default=False)
        monto = models.DecimalField(verbose_name="monto", null=True, blank=True, max_digits=10, decimal_places=2)
        datos = models.ForeignKey('sitio.Solicitud', on_delete=models.CASCADE, related_name="Solicitudes")
        pagos = models.ManyToManyField('sitio.Pago', related_name='pagos', blank=True)

        class Meta:
                verbose_name = 'Afiliado'
                verbose_name_plural = 'Afiliados'

        def fin_de_carencia(self):
                fecha_final = self.fecha + relativedelta(months=self.datos.plan.vigencia)
                self.fecha2 = fecha_final
                return self.fecha2

        def __str__(self):
                txt = "{}, {}, {}, {}"
                return txt.format(self.datos.apellido, self.datos.nombre, self.fecha.strftime("%d/%m/%Y"), self.numero)

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
		# slug = models.SlugField(max_length=150, unique=True, db_index=True)

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
                return txt.format(self.titulo, self.fecha.strftime("%d/%m/%Y-%H:%M"))

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
                                <span>%s</span>''' % (instance.nombre,
                                                      instance.email,
                                                      instance.numero,
                                                      instance.fecha.strftime('%d/%m/%Y %H:%M'),
                                                      instance.texto)
        nueva_notif.save()

### Notificacion de registros
@receiver(post_save, sender=PerfilUsuario)
def notif_registro(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "registro"
        nueva_notif.titulo = "Nuevo usuario registrado: %s" % instance.usuario
        nueva_notif.mensaje = '''<h2>NUEVO REGISTRO DE:</h2><p><strong>Nombre y apellido:</strong> %s</p><p><strong>Email:</strong> %s</p>
                                        <p>Fecha de registro: %s</p>
                              ''' % (instance.usuario, instance.nombre, timezone.now().strftime('%d/%m/%Y %H:%M'))
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
                                <p>Email: %s</p><p><strong>Fecha:</strong> %s</p>
                                ''' % (instance.apellido,
                                       instance.nombre,
                                       instance.dni,
                                       instance.telefono,
                                       instance.correo,
                                       instance.fecha.strftime('%d/%m/%Y %H:%M'))
        nueva_notif.save()

### Notificacion de Pagos
@receiver(post_save, sender=Pago)
def notif_pagos(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "pago"
        nueva_notif.titulo = "Nuevo pago registrado: %s" % instance.recibo_n
        nueva_notif.mensaje = '''<h2>%s</h2>
                                 <p><h3>$ %s</h3></p>
                                 <p><strong>%s</strong></p>
                                 <p><strong>Fecha:</strong> %s</p>''' % (instance.medio,
                                                                         instance.valor,
                                                                         instance.categoria.nombre,
                                                                         instance.fecha.strftime('%d/%m/%Y %H:%M'))
        nueva_notif.save()

### Notificacion de Regsitro de Usuario
@receiver(post_save, sender=User)
def notif_regisuser(sender, instance, **kwargs):
        nueva_notif = Notificaciones()
        nueva_notif.seccion = "usuario"
        nueva_notif.titulo = "Nuevo usuario registrado: %s" % instance.username
        nueva_notif.mensaje = '''<h2>%s</h2>
                                 <p><h3>%s</h3></p>
                                 <p><strong>Fecha de registro:</strong> %s</p>''' % (instance.username,
                                                                         instance.email,
                                                                         timezone.now().strftime('%d/%m/%Y %H:%M'))
        nueva_notif.save()
