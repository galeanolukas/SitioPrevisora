from django.forms import ModelForm,  Form, EmailField, CharField
#from .models import Post, Media, Comentario, AvisosyOtros, VideoChats
from django import forms
from .models import Contenido, Obituario, Saludo

class ContactoForm(Form):
    Correo = EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': '* CORREO ELECTRONICO'}))
    Nombre = CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '* NOMBRE'}))
    Mensaje = CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'DEJA TU CONSULTA..'}))
    
class FormContenido(ModelForm):
    class Meta:
        model = Contenido
        fields = ['titulo', 'categoria', 'texto', 'imagen', 'mostrar_img', 'fecha_post']

class FormHomenaje(ModelForm):
    class Meta:
        model = Obituario
        fields = ['nombre', 'edad', 'foto', 'texto', 'correo', 'mostrar', 'telefono', 'fecha_nac', 'fecha_falle']
        wdgets = {"nombre": forms.TextInput(attrs={"placeholder": "* NOMBRE COMPLETO"}),
                   "edad": forms.TextInput(attrs={"placeholder": "* EDAD"}),
                   "correo": forms.TextInput(attrs={"placeholder": "* CORREO ELECTRONICO"}),
		   "fecha_nac": forms.TextInput(attrs={"placeholder": "* FECHA DE NACIMIENTO"}),
                   "fecha_falle": forms.TextInput(attrs={"placeholder": "* FECHA DE FALLECIMIENTO"}),
                   "texto": forms.Textarea(attrs={'placeholder': 'Deja tu mensaje aqui..'}),
                   }

class FormSaludo(ModelForm):
    class Meta:
        model = Saludo
        fields = ['nombre', 'correo', 'texto', 'obituario']
        widgets = {"nombre": forms.TextInput(attrs={"placeholder": "NOMBRE"}),
                   "correo": forms.TextInput(attrs={"placeholder": "CORREO"}),
                   "texto": forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje o saludo..'}),
                   }
