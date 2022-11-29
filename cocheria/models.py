from django.db import models
from django.utils import timezone
from PaginaWeb.settings import DATE_INPUT_FORMATS
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

def subir_media(instance, filename):
	return "galeria/cocheria/" + filename
	
def subir_file(instance, filename):
	return "archivos/cocheria/" + filename

class Contenido(models.Model):
        opciones = (('Principal', 'Principal'),
                    ('Lateral', 'Lateral'), 
                    ('Servicios', 'Servicios'),
                    ('Noticias', 'Noticias'),
                    ('Galeria', 'Galeria'),
                    )
        titulo = models.CharField(max_length=80, null=True, blank=True)
        #orden = models.IntegerField()
        categoria = models.CharField(max_length=30, choices=opciones, null=True, blank=True)
        texto = RichTextUploadingField()
        imagen = models.FileField(upload_to=subir_media, null=True, blank=True)
        mostrar_img = models.BooleanField(default=True)
        fecha_post = models.DateTimeField(default=timezone.now, null=True, blank=True)
        
        def __str__(self):
                return str([self.titulo, self.categoria])
        
class Saludo(models.Model):
        nombre = models.CharField(max_length=100)
        texto = models.TextField(max_length=500)
        correo = models.EmailField()
        fecha = models.DateTimeField(null=True, blank=True)
        obituario = models.ForeignKey('cocheria.Obituario', on_delete=models.CASCADE, related_name='saludos', null=True, blank=True)

        def __str__(self):
                return str([self.nombre, self.fecha])


class Obituario(models.Model):
        nombre = models.CharField(max_length=100)
        edad = models.IntegerField()
        foto = models.FileField(upload_to=subir_media, null=True, blank=True)
        texto = RichTextUploadingField()
        correo = models.EmailField()
        telefono = models.IntegerField()
        mostrar = models.BooleanField(default=True)
        fecha_nac = models.DateField(null=True, blank=True)
        fecha_falle = models.DateField(null=True, blank=True)

        def __str__(self):
                return str([self.nombre, self.fecha_falle])


    
