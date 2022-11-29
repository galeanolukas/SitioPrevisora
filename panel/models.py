from django.db import models
from django.contrib.auth.models import User
from sitio.models import *

# Create your models here.

from django.utils import timezone


class RolDeUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rol')
    es_vendedor = models.BooleanField(default=False, verbose_name='Vendedor')
    es_administrativo = models.BooleanField(default=False, verbose_name='Administrativo')
    es_cobrador = models.BooleanField(default=False, verbose_name='Cobrador')

    def __unicode__(self):
        return u'(%s) %s' % (self.es_vendedor.verbose_name, self.es_administrativo.verbose_name)

    def mostrar_rol(self):
        if self.es_vendedor:
            return 'Vendedor'
        elif self.es_administrativo:
            return 'Administrativo'
        elif self.es_cobrador:
            return 'Cobrador'
        else:
            return 'Staff'

    def _str__(self):
        return self.mostrar_rol()

class ComisionesDeStaff(models.Model):
    rol = models.OneToOneField('RolDeUsuario', on_delete=models.CASCADE, related_name='rol')
    porcen_x_venta = models.IntegerField(default=0)
    porcen_x_afiliacion = models.IntegerField(default=0)
    porcen_x_cobros = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Comisiones x rol'
        verbose_name_plural = 'Comisiones del Staff'

    def __str__(self):
        return str(self.rol)

#Crear un registro de los movimientos de los Usuarios
class RegistroDeUsuarios(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    total_afiliaciones = models.IntegerField(default=0)
    total_pagos = models.IntegerField(default=0)
    total_cupones = models.IntegerField(default=0)
    total_compras = models.IntegerField(default=0)
    total_comision_x_mes = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_comision_x_semana = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_ingresos = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    fecha = models.DateTimeField(verbose_name='actualizado', default=timezone.now)

    class Meta:
        verbose_name = 'Actividad del usuario'
        verbose_name_plural = 'Regis. Actividad x Usuarios'

    def es_staff(self):
        if self.usuario.is_staff:
            return 'Staff'
        else:
            return 'Usuario'

    def __str__(self):
        return '%s (%s)' % (self.usuario.username, self.es_staff())

class RegistroTotalDeIngresos(models.Model):
    MESES = ((1, 'Enero'),
             (2, 'Febrero'),
             (3, 'Marzo'),
             (4, 'Abril'),
             (5, 'Mayo'),
             (6, 'Junio'),
             (7, 'Julio'),
             (8, 'Agosto'),
             (9, 'Septiembre'),
             (10, 'Octubre'),
             (11, 'Noviembre'),
             (12, 'Diciembre'))
    titulo = models.CharField(choices=MESES, verbose_name='mes', max_length=100)
    total_x_afiliaciones = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_x_pagos = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_x_compras = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    fecha_actual = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Ingreso del mes: '
        verbose_name_plural = 'Ingresos totales al Mes'

    def ala_fecha(self):
        return self.fecha.strftime('%Y')

    def actualizar(self, mes, afiliacion, pago, compra):
        if mes != self.fecha_actual.strftime('%m'):
            self.total_x_afiliaciones += afiliacion
            self.total_x_pagos += pago
            self.total_x_compras += compra

        else:
            pass


    def __str__(self):
        return self.titulo + ' de ' + ala_fecha

class TotalGeneralDeIngresos(models.Model):
    monto = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=20)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Ingresos totales a la Fecha'
        verbose_name_plural = verbose_name

    def __str__(self):
        return 'Ingreso un total de : ' + str(self.monto)


# Dirección IP y número de visitas al sitio web
class Userip(models.Model):
    ip=models.CharField(verbose_name='Dirección IP',max_length=30)    #ip address
    count=models.IntegerField(verbose_name='Visitas',default=0) # Las visitas ip
    class Meta:
        verbose_name = 'Acceder a la información del usuario'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.ip

#Total de visitas al sitio web
class VisitNumber(models.Model):
    count=models.IntegerField(verbose_name='Total de visitas al sitio web',default=0) #Total de visitas al sitio web
    class Meta:
        verbose_name = 'Total de visitas al sitio web'
        verbose_name_plural = verbose_name
    def __str__(self):
        return str(self.count)

##class RegistroVendedor(models.Model):
##    usuario = models.OneToOneField('auth.User',
##                                    on_delete=models.CASCADE,
##                                   related_name='vendedor', null=True, blank=True)
##

# Estadísticas de visitas de un día
class DayNumber(models.Model):
    day=models.DateField(verbose_name='Fecha',default=timezone.now)
    count=models.IntegerField(verbose_name='Número de visitas al sitio web',default=0) #Total de visitas al sitio web

    class Meta:
        verbose_name = 'Estadísticas de visitas diarias al sitio web'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.day)

# Registros de pagos x mes
class PagosxMes(models.Model):
    mes = models.CharField(max_length=10, verbose_name='Mes', default=timezone.now().strftime('%m/%Y'))
    total = models.IntegerField(blank=True, null=True)
    inf_pago = models.ForeignKey(Pago,
                                 on_delete=models.CASCADE,
                                 related_name="pago")

    class Meta:
        verbose_name = 'Pagos x mes'
        verbose_name_plural = 'Pagos del Mes'

    def __str__(self):
        return str(self.mes.strftime("%m/%Y"))

##Modelo mensajeria....
class Mensajes(models.Model):
    de = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emisor')
    para = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receptor')
    recibido = models.BooleanField(default=False)
    msj = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajeria interna'

    def __str__(self):
        return 'Mensaje de %s a %s' % (self.de, self.para)
