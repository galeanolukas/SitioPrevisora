"""PaginaWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.urls import path
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static, serve
import sitio, cocheria, clinicas, tienda, panel


urlpatterns = [
    path('', include('sitio.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('<path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('<path>', serve, {'document_root': settings.STATIC_ROOT}),
    path('cocheria/', include('cocheria.urls', namespace='cocheria')),
    path('salud/', include('clinicas.urls', namespace='clinicas')),
    path('tienda/', include('tienda.urls', namespace='tienda')),
    path('gestion/', include('panel.urls', namespace='panel-dash')),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'sitio.views.error_404'
