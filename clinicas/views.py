# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone, dateformat
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from .forms import ContactoForm, FormContenido
from .models import Contenido, Consultorio, Especialista

# Create your views here.

def home(request):
    posts_principal = Contenido.objects.filter(categoria__icontains="Principal")
    posts_lateral = Contenido.objects.filter(categoria__icontains="Lateral")
    return render(request, 'clinicas/home.html', {'principal':posts_principal, 'lateral':posts_lateral})

@login_required
def ver_panel(request):
    return render(request, 'clinicas/panel.html')

@login_required
def nuevo_contenido(request):
    if request.method == 'POST':
        contenido = FormContenido(request.POST, request.FILES)
        if contenido.is_valid():
            nuevo = contenido.save(commit=False)
            #post.autor = request.user
            nuevo.fecha_post = timezone.now()
            nuevo.save()
            return render(request, 'clinicas/mensaje.html', {'msj':'<h2>Se publico con exito!!</h2>'})
        else:
            print (contenido.errors)
            return render(request, 'clinicas/mensaje.html', {'msj':'<h2>Error!!</h2>'})
    else:
        contenido = FormContenido()

    return render(request, 'clinicas/publicar.html', {'form':contenido})

def mostrar_contenido(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    busqueda = request.GET.get('search', '')
    querys = (Q(categoria__icontains=busqueda) |
              Q(titulo__icontains=busqueda) |
              Q(id__icontains=busqueda)
             )
    if busqueda == "todas":
        post = Contenido.objects.all().order_by('-fecha_post')
    else:
        post = Contenido.objects.filter(querys).order_by('-fecha_post')
        
    return render(request, 'clinicas/ver.html', {'posteos':post, 'titulos':busqueda, 'imagenes':servicios})

@login_required
@permission_required('is_superuser')
def editar_contenido(request, ID):
    instancia = Contenido.objects.get(id=ID)
    if request.method == "POST":
        form = FormContenido(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            post = form.save(commit=False)
            #post.fecha_post = timezone.now()
            post.save()
            #return redirect('ver_post')
            return render(request, 'clinicas/mensaje.html', {'msj':'<h2>Post editado con exito!!</h2>'})
    else:
        form = FormContenido(instance=instancia)
        return render(request, 'clinicas/editar.html', {'form':form, 'post':instancia})


@login_required
@permission_required('is_superuser')
def borrar_contenido(request, ID):
        instancia = Contenido.objects.get(id=ID)
        instancia.delete()
        return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Se elimino el Post con exito!</h2>'})


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("/clinicas") 
