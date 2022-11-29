# -*- coding: utf-8 -*-
from django.forms import ModelForm,  Form, EmailField, CharField, IntegerField, DateField
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, User
from django import forms

class FormSolicitud(ModelForm):
    class Meta:
        model = Solicitud
        fields = ['nombre',
                  'apellido',
                  'dni',
                  'telefono',
                  'direccion',
                  'correo',
                  'plan',
                  ]
        
        widgets = {"nombre": forms.TextInput(attrs={"placeholder": "* NOMBRE"}),
                   "apellido": forms.TextInput(attrs={"placeholder": "* APELLIDO"}),
                   "direccion": forms.TextInput(attrs={"placeholder": "* DIRECCION"}),
                   "telefono": forms.TextInput(attrs={"placeholder": "* TELEFONO/CELULAR"}),
                   "correo": forms.TextInput(attrs={"placeholder": "* CORREO"}),
                   "dni": forms.TextInput(attrs={"placeholder": "* DNI"}),
                   "fecha_nac": forms.DateInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off', "placeholder": "* FECHA NAC D/M/A"}),
                   "fecha": forms.DateInput(attrs={"placeholder": " FECHA DE ALTA"}),
                   }
        

class FormPlanes(ModelForm):
    class Meta:
        model = Plan
        fields = ['titulo',
                  'periodo',
                  'vigencia',
                  'valor',
                  'descuento',
                  'servicio',
                  'total',
                  'descrip']

class FormCliente(ModelForm):
    class Meta:
        model = Cliente
        fields = ['usuario', 'numero', 'fecha', 'activo', 'datos', 'monto']

    
class FormContenido(ModelForm):
    class Meta:
        model = Contenido
        fields = ['titulo', 'categoria', 'texto', 'valor', 'imagen', 'mostrar_img', 'fecha_post']

        
##class FormPago(ModelForm):
##    class Meta:
##        model = Pago
##        fields = ['cliente', 'medio', 'recibo_n', 'valor', 'comprobante', 'fecha']
##        widgets = {'recibo_n':forms.TextInput(attrs={"type":"hidden"}),
##                   'medio':forms.TextInput(attrs={"type":"hidden"}),
##                   'fecha':forms.TextInput(attrs={"type":"hidden"}),
##                   'cliente':forms.TextInput(attrs={'type':'hidden'})
##                   }

class FormAviso(ModelForm):
    class Meta:
        model = Aviso
        fields = ['titulo', 'entrada', 'fecha']
        widgets = {"titulo": forms.TextInput(attrs={"placeholder": "* Titulo"}),
                   "entrada":forms.Textarea(attrs={'placeholder': 'Mensaje o aviso..'})
                   }

class FormPerfil(ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['usuario', 'telefono', 'ciudad', 'nombre']
        widgets = {"telefono": forms.TextInput(attrs={"placeholder": "* TELEFONO/CELULAR"}),
                   "nombre":forms.TextInput(attrs={'placeholder': '* NOMBRE Y APELLIDO'})}

class FormCupon(ModelForm):
    class Meta:
        model = Cupones
        fields = ['usuario', 'telefono', 'nombre', 'correo', 'numero_afiliado', 'numero_cupon']
        widgets = {"telefono": forms.TextInput(attrs={"placeholder": "* TELEFONO/CELULAR"}),
                   "numero_afiliado": forms.TextInput(attrs={"placeholder": "* NUMERO AFILIADO"}),
                   "correo": forms.TextInput(attrs={"placeholder": "CORREO ELECTRONICO"}),
                   "nombre":forms.TextInput(attrs={'placeholder': '* NOMBRE Y APELLIDO'})}
        
        
class FormRegistro(forms.Form):
    username = forms.CharField(label='USUARIO', min_length=4, max_length=150)
    email = forms.EmailField(label='CORREO')
    password1 = forms.CharField(label='CONTRASEÑA', widget=forms.PasswordInput)
    password2 = forms.CharField(label='REPITE CONTRASEÑA', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("El Usuario con ese correo ya existe!")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Correo electronico ya existe!")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Contraseña no coinciden!")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user

class EditUserForm(ModelForm):
         class Meta:
             model = User
             fields = (
                 'email',
                 'username',
                 'password',
                 'is_active',
                 'is_superuser'
                )

             widgets = {"password":forms.TextInput(attrs={"type":"password"})}
		
		
class ContactoForm(Form):
    Correo = EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': '* CORREO ELECTRONICO'}))
    Telefono = IntegerField(required=True, max_value=10, widget=forms.TextInput(attrs={'placeholder':'TELEFONO/CELULAR'}))
    Nombre = CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '* NOMBRE COMPLETO'}))
    Mensaje = CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'Deja tu mensaje o consulta..'}))
