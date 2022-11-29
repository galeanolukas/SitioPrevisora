from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required, permission_required
from .models import Category, Product, OrderItem, Order
from .forms import CartAddProductForm, OrderCreateForm
from .cart import Cart
from sitio.utils import *
from sitio.models import MercadoPagoData
import mercadopago

def product_list(request, category_slug=None):
    categorias = Category.objects.all()
    categoria = None
    productos = Product.objects.filter(disponible=True)
    if category_slug:
        categoria = get_object_or_404(Category, slug=category_slug)
        productos = Product.objects.filter(categoria=categoria)

    context = {
        'category': categoria,
        'categories': categorias,
        'products': productos,
        'name-search':'buscar',
    }

    return render(request, 'tienda/product/inicio.html', context)

##
def product_detail(request, id, product_slug):
    categorias = Category.objects.all()
    producto = get_object_or_404(Product, id=id, slug=product_slug, disponible=True)
    carrito_product_form = CartAddProductForm()
    context = {
        'product': producto,
        'cart_product_form': carrito_product_form,
        'categories': categorias,
    }

    print (producto)

    return render(request, 'tienda/product/detail.html', context)

@login_required(login_url='/#ingresar')
def order_create(request):
    carrito = Cart(request)
    monto_total = 0
    num_productos = 0
    preference_data = {"items":[]}
    categorias = Category.objects.all()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.usuario = request.user
            orden.save()
            for item in carrito:
                OrderItem.objects.create(
                    orden=orden,
                    producto=item['producto'],
                    precio=item['precio'],
                    cantidad=item['cantidad']
                )

            mp = MPCheckOut(MercadoPagoData.objects.get(nombre="PrevisoraPagos"))
            # mp = MercadoPagoData.objects.get(nombre="PrevisoraPagos")
            # sdk = mercadopago.SDK(mp.access_token)

            orden_reciente = Order.objects.get(id=orden.id)

            for producto in orden_reciente.items.all():
                monto_total += int(producto.precio)
                num_productos += 1
                mp.config(monto=float(producto.precio),
                          titulo=producto.producto.nombre,
                          unidad=producto.cantidad)
            #     preference_data["items"].append({ "title": producto.producto.nombre,
            #                                       "quantity": producto.cantidad,
            #                                       "unit_price": float(producto.precio), })
            #
            # preference_response = sdk.preference().create(preference_data)
            # preference = preference_response["response"]
            # print (preference)

            carrito.clear()
            return render(request, 'tienda/order/created.html', {'order': orden, 'mp_boton': mp.boton()})

    else:
        form = OrderCreateForm()

    return render(request, 'tienda/order/create.html', {'form': form, 'categories':categorias})


@require_POST
def cart_add(request, product_id):
    carrito = Cart(request)  # create a new cart object passing it the request object
    producto = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        carrito.add(product=producto,
                    quantity=cd['cantidad'],
                    cuotas=cd['cuotas'],
                    update_quantity=cd['actualizado'])

    return redirect('tienda:cart_detail')

def cart_remove(request, product_id):
    carrito = Cart(request)
    producto = get_object_or_404(Product, id=product_id)
    carrito.remove(producto)

    return redirect('tienda:cart_detail')

@login_required(login_url='/#ingresar')
def shop_now(request, product_id):
    carrito = Cart(request)
    carrito.clear()
    producto = get_object_or_404(Product, id=product_id)
    carrito.add(product=producto, quantity=1, update_quantity=False)

    return redirect('tienda:order_create')


def cart_detail(request):
    categorias = Category.objects.all()
    carrito = Cart(request)
    for item in carrito:
        item['update_quantity_form'] = CartAddProductForm(initial={'cantidad': item['cantidad'], 'actualizado': True})

##    print (carrito)
####    return render(request, 'tienda/detail.html', {'mi_carrito': carrito})
    return render(request, 'tienda/detail.html', {'mi_carrito': carrito, 'categories':categorias})

def pay_view(request, orden_num):
    monto_total = 0
    num_productos = 0
    productos = []
    orden = Order.objects.get(id=orden_num)
    orden.pagado = True
    for producto in orden_reciente.items.all():
        monto_total += int(producto.precio)
        num_productos += 1
        productos.append(producto.nombre)


    return render(request, 'tienda/pago_api.html')
