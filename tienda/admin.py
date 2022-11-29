from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Promo

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}



class ProductAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'precio', 'stock', 'disponible', 'creado_al', 'actualizado_al']
    list_filter = ['disponible', 'creado_al', 'actualizado_al']
    list_editable = ['precio', 'stock', 'disponible']
    prepopulated_fields = {'slug': ('nombre',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['producto']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'direccion', 'pagado', 'numero_afiliado', 'creado', 'actualizado']
    list_filter = ['pagado', 'creado', 'actualizado']
    inlines = [OrderItemInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Promo)
