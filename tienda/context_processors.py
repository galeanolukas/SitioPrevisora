from .cart import Cart


def cart(request):
    return {'carrito': Cart(request)}

