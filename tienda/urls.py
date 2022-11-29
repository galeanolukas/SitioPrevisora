from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static, serve


app_name = 'tienda'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('orden/', views.order_create, name='order_create'),
    path('orden/rapida/<product_id>/', views.shop_now, name='shop_now'),
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('<path>', serve, {'document_root': settings.MEDIA_ROOT}), 
    path('<path>', serve, {'document_root': settings.STATIC_ROOT}),
    path('carrito/agregar/<product_id>/', views.cart_add, name='cart_add'),
    path('mercadopago/<orden_num>/', views.pay_view, name="pagar_mp"),
    path('carrito/remover/<product_id>/', views.cart_remove, name='cart_remove'),
    path('<category_slug>/', views.product_list, name='product_list_by_category'),
    path('<id>/<product_slug>/', views.product_detail, name='product_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
