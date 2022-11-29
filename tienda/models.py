from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from sitio.models import MercadoPagoData


class Category(models.Model):
    nombre = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    icon = models.CharField(max_length=150, null=True, blank=True)
    creado_al = models.DateTimeField(auto_now_add=True)
    actualizado_al = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('nombre', )
        verbose_name = 'categoria'
        verbose_name_plural = 'Categorias de los productos'

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('tienda:product_list_by_category', args=[self.slug])


class Product(models.Model):
    categoria = models.ForeignKey(Category, related_name='productos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    descripcion = RichTextUploadingField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    cuotas = models.IntegerField(default=1)
    interes = models.IntegerField(verbose_name='interes por cuotas', default=0)
    creado_al = models.DateTimeField(auto_now_add=True)
    actualizado_al = models.DateTimeField(auto_now=True)
    vendedor = models.ForeignKey(MercadoPagoData, related_name='cuenta_mp', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/%Y/%m/%d', blank=True)

    class Meta:
        ordering = ('nombre', )
        index_together = (('id', 'slug'),)
        verbose_name = 'producto'
        verbose_name_plural = 'Productos'

    def valor_de_cuotas(self):
        if self.cuotas > 1:
            interes = (self.precio * self.interes) / 100
            return int((self.precio + interes) / self.cuotas)
        else:
            return self.precio

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('tienda:product_detail', args=[self.id, self.slug])


class Promo(models.Model):
    producto = models.ForeignKey(Product, related_name="promo", on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    creado_al = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'promo'
        verbose_name_plural = 'Promociones'

    def __str__(self):
        return str(self.producto)

class Order(models.Model):
    usuario = models.ForeignKey("auth.User", related_name='usuario', on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=100, verbose_name="nombre y apellido")
    dni = models.IntegerField(verbose_name='numero de dni')
    telefono = models.IntegerField(verbose_name="telefono/celular")
    numero_afiliado = models.IntegerField(verbose_name="afliliado numero", blank=True, null=True)
    email = models.EmailField(blank=True, verbose_name="correo electronico", null=True)
    direccion = models.CharField(max_length=150, verbose_name="direccion")
    #codigo_postal = models.CharField(max_length=30, verbose_name="")
    #ciudad = models.CharField(max_length=100, verbose_name="")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True, null=True)
    pagado = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ('-creado', )
        verbose_name = 'orden'
        verbose_name_plural = 'Ordenes de compras'

    def __str__(self):
        return 'Orden de compra {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    orden = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cuotas = models.PositiveIntegerField(default=1, null=True, blank=True)
    valor_cuota = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.precio * self.cantidad
