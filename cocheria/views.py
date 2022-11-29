# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.db.models import Q
from PaginaWeb.settings import DATE_INPUT_FORMATS, EMAIL_HOST_USER, TIME_ZONE, NOTIF_EMAIL, ALLOWED_HOSTS
from django.contrib.auth.decorators import login_required, permission_required
from .forms import ContactoForm, FormContenido, FormHomenaje, FormSaludo
from .models import Contenido, Obituario
from sitio.models import Contacto
from .msjhtml import plantilla
# Create your views here.

def home(request):
    principal = Contenido.objects.filter(categoria="Principal")
    noticias = Contenido.objects.filter(categoria="Noticias")
    lateral = Contenido.objects.filter(categoria="Lateral")
    post = Obituario.objects.all().order_by('-fecha_falle')
    return render(request, 'cocheria/home.html', {'principal':principal, 'noticias':noticias, 'lateral':lateral, 'obituarios':post})

def servicios(request):
    posts = Contenido.objects.filter(categoria="Servicios")
    return render(request, 'cocheria/servicios.html', {"contenido": posts})

@login_required
def ver_panel(request):
    return render(request, 'cocheria/panel.html')

def homenajes(request):
    busqueda = request.GET.get('n')
    xnombre = request.GET.get('xnombre')
    print (xnombre)
    x_nombre_id = None
    obituario = None
    if request.method == 'POST':
        post = Obituario.objects.get(nombre=busqueda)
        form = FormSaludo(request.POST)
        print (busqueda)
        if form.is_valid:
            instancia = form.save(commit=False)
            instancia.fecha = timezone.now()
            instancia.Obituario = post
            instancia.save()
            mensaje = [post.foto.url, instancia.texto, instancia.nombre]

            try:
                mail2 = EmailMultiAlternatives("COCHERIA SAN FRANCISCO", plantilla(mensaje), [EMAIL_HOST_USER], [post.correo])
                mail2.attach_alternative(plantilla(mensaje), "text/html")
                mail2.send()

            except BadHeaderError:
                pass
    else:
        if busqueda == "all":
            post = Obituario.objects.all().order_by('-id').filter(mostrar=True)
            print (post)
            
        elif xnombre:
            post = Obituario.objects.filter(Q(nombre__icontains=xnombre))
            if post:
                if len(post) > 1:
                    pass
                else:
                    return redirect('/cocheria/homenajes/?n=all#%s' % str(post[0].id + 1))
            else:
                pass
                
        else:
            try:
                post = Obituario.objects.get(nombre=busqueda)
                
            except Obituario.DoesNotExist:
                post = []


        form = FormSaludo()
        
    return render(request, 'cocheria/homenajes.html', {'obituarios': post, 'obituario': post, 'form':form})
      
def vista_contacto(request):
    mensaje = '<h2>Hemos recibido tu mensaje con exito!!</h2><p>Gracias por contactarnos, recibiras una respuesta muy pronto.</p>'
    if request.method == 'GET':
        form = ContactoForm()
    else:
        form = ContactoForm(request.POST)
        if form.is_valid():
            registro = Contacto()
            subject = form.cleaned_data['Nombre']
            from_email = form.cleaned_data['Correo']
            message = form.cleaned_data['Mensaje']
            registro.nombre = subject
            registro.email = from_email
            registro.mensaje = message
            try:
                send_mail(subject, message, from_email, [EMAIL_HOST_USER, NOTIF_EMAIL])
                registro.save()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
            return render(request, 'cocheria/mensaje.html', {'msj':mensaje})
    return render(request, "cocheria/contacto.html", {'form': form})

@login_required
def nuevo_contenido(request):
    if request.method == 'POST':
        contenido = FormContenido(request.POST, request.FILES)
        if contenido.is_valid():
            nuevo = contenido.save(commit=False)
            #post.autor = request.user
            nuevo.fecha_post = timezone.now()
            nuevo.save()
            return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Se publico con exito!!</h2>'})
        else:
            print (contenido.errors)
            return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Error!!</h2>'})
    else:
        contenido = FormContenido()

    return render(request, 'cocheria/publicar.html', {'form':contenido})

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
        
    return render(request, 'cocheria/ver.html', {'posteos':post, 'titulos':busqueda, 'imagenes':servicios})

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
            return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Post editado con exito!!</h2>'})
    else:
        form = FormContenido(instance=instancia)
        return render(request, 'cocheria/editar.html', {'form':form, 'post':instancia})


@login_required
@permission_required('is_superuser')
def crear_obituario(request):
    if request.method == "POST":
        form = FormHomenaje(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Se creo obituario con exito!!</h2>'})
    else:
        form = FormHomenaje()

    return render(request, 'cocheria/homenaje.html', {'form':form})
    

@login_required
@permission_required('is_superuser')
def editar_obituario(request, ID):
    instancia = Obituario.objects.get(id=ID)
    if request.method == "POST":
        form = FormHomenaje(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            post = form.save(commit=False)
            #post.fecha_post = timezone.now()
            post.save()
            #return redirect('ver_post')
            return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Post editado con exito!!</h2>'})
    else:
        form = FormHomenaje(instance=instancia)

    return render(request, 'cocheria/editar.html', {'form':form, 'post':instancia})

@login_required
@permission_required('is_superuser')
def borrar_contenido(request, ID):
        instancia = Contenido.objects.get(id=ID)
        instancia.delete()
        return render(request, 'cocheria/mensaje.html', {'msj':'<h2>Se elimino el Post con exito!</h2>'})

@login_required
@permission_required('is_superuser')
def borrar_obi(request, ID):
        instancia = Obituario.objects.get(id=ID)
        instancia.delete()
        return render(request, 'sitio/mensaje.html', {'msj':'<h2>Se elimino el Post con exito!</h2>'})

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("/cocheria") 
