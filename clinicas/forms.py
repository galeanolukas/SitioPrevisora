from django.forms import ModelForm,  Form, EmailField, CharField
#from .models import Post, Media, Comentario, AvisosyOtros, VideoChats
from django import forms
from .models import Contenido, Consultorio, Especialista, Agenda 

class ContactoForm(Form):
    Correo = EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': '* CORREO ELECTRONICO'}))
    Nombre = CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '* NOMBRE'}))
    Mensaje = CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'DEJA TU CONSULTA..'}))
    
class FormContenido(ModelForm):
    class Meta:
        model = Contenido
        fields = ['titulo', 'categoria', 'texto', 'imagen', 'fecha_post']

class FormAgenda(ModelForm):
    class Meta:
        model = Agenda
        fields = ['profesional', 'horario_inicio', 'horario_final', 'dias']
        #widget = {'dias', forms.CheckboxSelectMultiple}
