from decimal import Decimal
from django.conf import settings
from tienda.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False, cuotas=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            if cuotas:
                self.cart[product_id] = {'cantidad': 0, 'precio': str(product.valor_de_cuotas())}
            else:
                self.cart[product_id] = {'cantidad': 0, 'precio': str(product.precio)}
        if update_quantity:
            self.cart[product_id]['cantidad'] = quantity
        else:
            self.cart[product_id]['cantidad'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        productos = Product.objects.filter(id__in=product_ids)
        for producto in productos:
            self.cart[str(producto.id)]['producto'] = producto

        for item in self.cart.values():
            item['precio'] = Decimal(item['precio'])
            item['precio_total'] = item['precio'] * item['cantidad']
            yield item

    def __len__(self):
        return sum(item['cantidad'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
