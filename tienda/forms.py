from django import forms
from .models import Order, Product


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]


class CartAddProductForm(forms.Form):
    cantidad = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    cuotas = forms.BooleanField(required=False, initial=False)
    actualizado = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['nombre',
                  'dni',
                  'telefono',
                  'email',
                  'direccion',
                  'numero_afiliado']

        widgets = {"telefono": forms.TextInput(attrs={"placeholder": "* TELEFONO/CELULAR"}),
                   "numero_afiliado": forms.TextInput(attrs={"placeholder": "NUMERO AFILIADO", 'type':'number'}),
                   "dni":forms.TextInput(attrs={"placeholder": "* NUMERO DE DNI", 'type':'number'}),
                   "email": forms.TextInput(attrs={"placeholder": "CORREO ELECTRONICO"}),
                   "nombre":forms.TextInput(attrs={'placeholder': '* NOMBRE COMPLETO'}),
                   "direccion":forms.TextInput(attrs={'placeholder': '* DIRECCION'}),

                   }

class FormProducto(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre',
                  'categoria',
                  'precio',
                  'stock',
                  'imagen',
                  'cuotas',
                  'descripcion',
                  'disponible']
