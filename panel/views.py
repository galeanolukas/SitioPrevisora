from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.shortcuts import render, redirect, HttpResponse
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages #import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from PaginaWeb.settings import DATE_INPUT_FORMATS, EMAIL_HOST_USER, TIME_ZONE, NOTIF_EMAIL
from dateutil.relativedelta import relativedelta
from .models import *
from sitio.msjhtml import plantilla
from sitio.models import *
from tienda.models import *
from tienda.forms import FormProducto
from sitio.forms import *
from django.utils import timezone
from django import template
from sitio.utils import render2pdf, MPCheckOut, Key

# Create your views here.

@register.filter(name='llave')
def llave(d, index):
    return list(d)[index]

@register.filter(name='valor')
def valor(d, index):
    return mark_safe(d[list(d)[index]])

### Pagina de inicio del panel
@login_required
def home(request):
    data = dash_card_content(request)
    if request.user.is_superuser:
        data['info_usuarios'] = User.objects.order_by('-last_login')

    else:
        if request.user.rol.es_administrativo:
            pass
        elif request.user.rol.es_cobrador:
            pass
        pass
    return render(request, 'panel/home.html', data)


@login_required
def mov_del_sitio(request):
    return render(request, 'panel/detalles.html')
#Muestra las cards de informacion
#Define el contenido a mostrar del dash por usuario logueado
def dash_card_content(request):
    usuario_actual = request.user
    request_datos = actualizar_datos(request)
    notifs = Notificaciones.objects.all().filter(activa=True).order_by('-id')
    data = {}

    if usuario_actual.is_superuser:
        name_icons = {
                          'Visitas al Sitio':'<ion-icon name="eye-outline"></ion-icon>',
                          'Registrados':'<ion-icon name="people-outline"></ion-icon>',
                          'Cupones de Sorteos':'<ion-icon name="ticket-outline"></ion-icon>',
                          'Total de Ingresos':'<ion-icon name="cash-outline"></ion-icon>',
                          'Total de Afiliados':'<ion-icon name="people-circle-outline"></ion-icon>',
                          }

        data = {'nameandicons':name_icons,
                    'caja_uno': request_datos['total_visitas'],
                    'caja_dos': request_datos['total_usuarios'],
                    'conteo_dos':'Staff: %s' % request_datos['total_usuarios_staff'],
                    'caja_cuatro':'$ %s' % request_datos['ingresos_totales'],
                    'conteo_cuatro': 'Pagos: %s' % request_datos['cantidad_pagos'],
                    'caja_tres': request_datos['total_cupones'],
                    'conteo_uno': 'Hoy: %s' % request_datos['total_visitas_hoy'],
                    'caja_cinco':request_datos['total_afiliaciones'],
                    'conteo_cinco':'Activos: %s' % request_datos['total_afiliaciones_activos'],
                    'notifs': notifs,
                    'hoy': timezone.now}

    elif usuario_actual.is_staff:
        if usuario_actual.rol.es_vendedor:
            name_icons = {
                          'Afiliaciones':'<ion-icon name="people-circle-outline"></ion-icon>',
                          'Solicitudes':'<ion-icon name="people-outline"></ion-icon>',
                          'Cupones de Sorteo':'<ion-icon name="ticket-outline"></ion-icon>',
                          'Recaudado':'<ion-icon name="cash-outline"></ion-icon>',
                          'Comisiones':'<ion-icon name="wallet-outline"></ion-icon>'
                          }

        elif usuario_actual.rol.es_cobrador:
            name_icons = {
                          'Afiliaciones':'<ion-icon name="people-circle-outline"></ion-icon>',
                          'Solicitudes':'<ion-icon name="people-outline"></ion-icon>',
                          'Cupones de Sorteo':'<ion-icon name="ticket-outline"></ion-icon>',
                          'Recaudado':'<ion-icon name="cash-outline"></ion-icon>',
                          'Comisiones':'<ion-icon name="wallet-outline"></ion-icon>'
                          }

        elif usuario_actual.rol.es_administrativo:
            name_icons = {
                          'Afiliaciones':'<ion-icon name="people-circle-outline"></ion-icon>',
                          'Solicitudes':'<ion-icon name="people-outline"></ion-icon>',
                          'Cupones de Sorteo':'<ion-icon name="ticket-outline"></ion-icon>',
                          'Recaudado':'<ion-icon name="cash-outline"></ion-icon>',
                          'Comisiones':'<ion-icon name="wallet-outline"></ion-icon>'
                          }

        data = {'nameandicons':name_icons,
                    'caja_uno': request_datos['total_afiliaciones'],
                    'caja_dos': request_datos['total_solicitudes'],
                    'caja_tres': request_datos['total_cupones'],
                    'caja_cuatro':request_datos['ingresos_totales'],
                    'caja_cinco':0,
                    'hoy': timezone.now,
                    }

    else:
        name_icons = {
                      'Solicitudes':'<ion-icon name="id-card-outline"></ion-icon>',
                      'Planes':'<ion-icon name="people-circle-outline"></ion-icon>',
                      'Cupones de Sorteo':'<ion-icon name="ticket-outline"></ion-icon>',
                      'Tus Pagos':'<ion-icon name="cash-outline"></ion-icon>',
                      'Beneficios':'<ion-icon name="ticket-outline"></ion-icon>',
                     }



        data = {
             'nameandicons':name_icons,
             'caja_uno': request_datos['total_solicitudes'],
             'caja_dos': request_datos['total_afiliaciones'],
             'caja_tres': request_datos['total_cupones'],
             'caja_cuatro':request_datos['cantidad_pagos'],
             'caja_cinco':0,
             'hoy': timezone.now,
              }

    return data

#================================================================================
#FUNCION QUE RECOBRA DATOS
def actualizar_datos(request):
    total_ingresos = 0
    total_pagos = 0
    info_usuario = None
    total_usuarios = 0
    total_usuarios_staff = 0
    total_afiliaciones = 0
    total_afiliaciones_activos = 0
    total_solicitudes = 0
    total_cupones = 0
    total_visitas = 0
    total_visitas_hoy = 0
    total_cupones = 0
    pagos = Pago.objects.all()
    cupones = Cupones.objects.all()
    solicitudes = Solicitud.objects.all()
    afiliaciones = Cliente.objects.all()
    mensajes = Mensajes.objects.all()
    usuarios = User.objects.all()
    usuario_actual = request.user
    #Busca al usuario en el registro sino lo encuentra crea un nuevo
    try:
        registro_usuario = RegistroDeUsuarios.objects.get(usuario=usuario_actual)
    except:
        registro_usuario = RegistroDeUsuarios()
        registro_usuario.usuario = usuario_actual
        registro_usuario.save()

    #Si el login es un superusuario obtiene datos generales
    if usuario_actual.is_superuser:
        for pago in pagos:
            total_ingresos += float(pago.valor)

        total_pagos = pagos.count()
        total_usuarios = usuarios.count()
        total_usuarios_staff = usuarios.filter(is_staff=True).count()
        total_visitas = VisitNumber.objects.all()[0].count
        total_afiliaciones = afiliaciones.count()
        total_afiliaciones_activos = afiliaciones.filter(activo=True).count()
        try:
            total_visitas_hoy = DayNumber.objects.get(day=timezone.now().date()).count
        except:
            total_visitas_hoy = 0

        try:
            registro_ingresos_total = TotalGeneralDeIngresos.objects.all()[0]
        except:
            registro_ingresos_total = TotalGeneralDeIngresos()
            pass

        total_cupones = cupones.count()
        registro_ingresos_total.monto = total_usuarios
        registro_ingresos_total.save()

    elif usuario_actual.is_staff:
        if usuario_actual.rol.es_vendedor:
            total_cupones = cupones.filter(usuario=usuario_actual).count()
            total_solicitudes = solicitudes.filter(usuario=usuario_actual).count()
            try:
                pagos_x_usuario = pagos.filter(usuario=usuario_actual)
                #suma la cantidad de cobros por usuarios
                for pago in pagos_x_usuarios:
                    total_ingresos += float(pago.valor)

                total_pagos = pagos_x_usuario.count()

            except:
                pass

        elif usuario_actual.rol.es_cobrador:
            total_cupones = cupones.filter(usuario=usuario_actual).count()
            total_solicitudes = solicitudes.filter(usuario=usuario_actual).count()

            try:
                pagos_x_usuario = pagos.filter(usuario=usuario_actual)
                for pago in pagos_x_usuarios:
                    total_ingresos += float(pago.valor)

                total_pagos = pagos_x_usuario.count()
            except:
                pass

        elif usuario_actual.rol.es_administrativo:
            total_cupones = cupones.filter(usuario=usuario_actual).count()
            total_solicitudes = solicitudes.filter(usuario=usuario_actual).count()
            try:
                pagos_x_usuario = pagos.filter(usuario=usuario_actual)
                for pago in pagos_x_usuarios:
                    total_ingresos += float(pago.valor)
                    total_pagos = pagos_x_usuario.count()
            except:
                pass
    #Excepcio en caso de ser usuario comun
    else:
        total_cupones = cupones.filter(usuario=usuario_actual).count()
        total_solicitudes = solicitudes.filter(usuario=usuario_actual).count()
        try:
            pagos_x_usuario = pagos.get(usuario=usuario_actual)
            for pago in pagos_x_usuarios:
                total_ingresos += float(pago.valor)

            total_pagos = pagos_x_usuario.count()
        except:
            pass



    registro_usuario.total_ingresos = total_ingresos
    registro_usuario.total_pagos = total_pagos
    registro_usuario.total_cupones = total_cupones
    registro_usuario.save()

    return {'ingresos_totales':total_ingresos,
            'cantidad_pagos':total_pagos,
            'total_usuarios':total_usuarios,
            'total_usuarios_staff':total_usuarios_staff,
            'total_afiliaciones':total_afiliaciones,
            'total_afiliaciones_activos':total_afiliaciones_activos,
            'total_solicitudes':total_solicitudes,
            'total_cupones':total_cupones,
            'total_visitas':total_visitas,
            'total_visitas_hoy':total_visitas_hoy,
            'info_usuario':info_usuario,
            }

@permission_required('is_staff')
def ver_mensajes(request):
    data = dash_card_content(request)
    contactos = Contacto.objects.all().order_by('-fecha')
    contacto = None
    search = 'msj-data'
    if request.method == 'POST':
        try:
            busqueda = request.POST[search]
            print (busqueda)
            querys = (Q(id__icontains=busqueda) |
                  Q(nombre__icontains=busqueda) |
                  Q(email__icontains=busqueda)
                )
            contactos = contactos.filter(querys)
        except:
            pass

    else:
        try:
            busqueda = request.GET['id']
            contacto = Contacto.objects.get(id=busqueda)

        except:
            pass

    data['mensaje'] = contacto
    data['mensajes'] = contactos
    data['ultimo_msj'] = Contacto.objects.all().last()
    data['name_search'] = search

    return render(request, 'panel/consulta-msj.html', data)

# Pagar
def pagos_online(request):
    pass

# @permission_required('is_staff')
def mostrar_msj(request, ID=None):
    data = dash_card_content(request)
    recibidos = Mensajes.objects.all().filter(para=request.user).order_by('-fecha')
    if request.method == 'POST':
        if ID:
            msj_selec = Mensajes.objects.get(id=ID)
        else:
            pass

    else:
        if ID:
            msj_selec = Mensajes.objects.get(id=ID)

        else:
            pass

    data['buzon_recibidos'] = mensajes

    return render(request, 'panel/mensajeria.html', data)

# Panel
@login_required
def consulta_x_registros(request, tp):
    busqueda = False
    resultados = None
    resultado = None
    form = None
    search = 'regist-search'
    data = dash_card_content(request)

    if request.method == "POST":
        busqueda = request.POST[search]
        print (busqueda)

        if tp == 'afiliados':
            querys = (Q(id__icontains=busqueda) |
                  Q(monto__icontains=busqueda) |
                  Q(datos__nombre__icontains=busqueda) |
                  Q(datos__correo__icontains=busqueda) |
                  Q(usuario__username__icontains=busqueda)
                )

            resultados = Cliente.objects.all().order_by('-fecha').filter(querys)

        elif tp == 'solicitudes':
            querys = (Q(id__icontains=busqueda) |
                  Q(dni__icontains=busqueda) |
                  Q(nombre__icontains=busqueda) |
                  Q(apellido__icontains=busqueda) |
                  Q(correo__icontains=busqueda) |
                  Q(usuario__username__icontains=busqueda)
                )
            resultados = Solicitud.objects.all().order_by('-fecha').filter(querys)


        elif tp == 'usuarios':
            querys = (Q(id__icontains=busqueda) |
                  Q(first_name__icontains=busqueda) |
                  Q(last_name__icontains=busqueda) |
                  Q(email__icontains=busqueda) |
                  Q(username__icontains=busqueda)
                )
##
            resultados = User.objects.all().order_by('-last_login').filter(querys)

        elif tp == 'pagos':
            querys = (Q(id__icontains=busqueda) |
                  Q(categoria__nombre__icontains=busqueda) |
                  Q(categoria__codigo__icontains=busqueda) |
                  Q(recibo_n__icontains=busqueda) |
                  Q(valor__icontains=busqueda)
                )

            resultados = Pago.objects.all().order_by('-fecha').filter(querys)
        else:
            pass


    else:
        try:
            if tp == 'afiliados':
                resultado = Cliente.objects.get(id=request.GET['id'])
                #actualiza el plazo de carencia
                print (resultado.fin_de_carencia())

            elif tp == 'solicitudes':
                resultado = Solicitud.objects.get(id=request.GET['id'])
            elif tp == 'usuarios':
                resultado = User.objects.get(id=request.GET['id'])
            elif tp == 'pagos':
                resultado = Pago.objects.get(id=request.GET['id'])
            else:
                pass

        except:
            pass

        if tp == 'afiliados':
            resultados = Cliente.objects.all().order_by('-fecha')
            form = FormCliente()
        elif tp == 'solicitudes':
            resultados = Solicitud.objects.all().order_by('-fecha')
            form = FormSolicitud(initial={'usuario':request.user})
        elif tp == 'usuarios':
            resultados = User.objects.all().order_by('-last_login')
            form = FormRegistro()
        elif tp == 'pagos':
            resultados = Pago.objects.all().order_by('-fecha')
            form = PagoForm(initial={'usuario': request.user})

        else:
            pass

    pdf = render2pdf('panel/registros.html', {'resultado':resultado, 'estado':tp})
    print (pdf)

    data['estado'] = tp
    data['resultado'] = resultado
    data['resultados'] = resultados
    data['name_search'] = search
    data['pdf'] = pdf
    data['form'] = form


    return render(request, 'panel/consulta-registros.html', data)

### Editar los regitros
@login_required
@permission_required('is_superuser')
def editar_registro(request, tp, ID=None):
    data = dash_card_content(request)
    if tp == 'solicitud' and ID > 0:
        instancia = Solicitud.objects.get(id=ID)
    elif tp == 'afiliado' and ID > 0:
        instancia = Cliente.objects.get(id=ID)
    elif tp == 'usuario' and ID > 0:
        instancia = User.objects.get(id=ID)
    else:
        pass

    if request.method == "POST":
        if tp == 'solicitud':
            if ID == 0:
                form = FormSolicitud(request.POST, request.FILES)
            else:
                form = FormSolicitud(request.POST, request.FILES, instance=instancia)

        elif tp == 'afiliado':
            if ID == 0:
                form = FormCliente(request.POST, request.FILES)
            else:
                form = FormCliente(request.POST, request.FILES, instance=instancia)

        elif tp == 'usuario':
            if ID == 0:
                form = EditUserForm(request.POST, request.FILES)
            else:
                form = EditUserForm(request.POST, request.FILES, instance=instancia)
        else:
            pass

        if form.is_valid():
            post = form.save(commit=False)
            if ID == 0:
                post.usuario = request.user
                mensaje = '%s creado con exito!!'
            else:
                mensaje = '%s se edito con exito!!'

            post.save()
            messages.success(request, mensaje % tp)
            return redirect('panel:editar_r', tp=tp, ID=ID)
        else:
            mensaje = 'Error al procesar la informacion'
            pass
    else:
        if ID != 0:
            if tp == 'solicitud':
                form = FormSolicitud(instance=instancia)
            if tp == 'afiliado':
                form = FormCliente(instance=instancia)
            if tp == 'usuario':
                form = EditUserForm(instance=instancia)
        else:
            pass

        data['selec'] = tp
        data['form'] = form
        data['post'] = instancia

    return render(request, 'panel/editar.html', data)

##Eliminar registros
@login_required
@permission_required('is_superuser')
def eliminar_registro(request, tp, ID):
    msj_nuevo = 'Se elimino %s con exito!!!'

    if tp == 'afiliado':
        afiliado = Cliente.objects.get(id=ID)
        afiliado.datos.aprobada = False
        afiliado.datos.save()
        afiliado.delete()

    elif tp == 'solicitud':
        solicitud = Solicitud.objects.get(id=ID)
        solicitud.delete()

    elif tp == 'usuario':
        usuario = User.objects.get(id=ID)
        usuario.delete()

    elif tp == 'mensaje':
        mensaje = Contacto.objects.get(id=ID)
        mensaje.delete()

    else:
        messages.error(request, 'fallo al eliminar %s' % tp)
        return redirect('/#msg')

    messages.success(request, msj_nuevo % tp)
    print (request.path)
    return redirect("/gestion/mensajes/#msg")   # from django.http import HttpResponseRedirect

# Notificaciones del sitio
@permission_required('is_staff')
def mostrar_notif(request):
    data = dash_card_content(request)
    notificacion = None
    try:
        notif_id = request.GET['n']
        print (notif_id)
        notificacion = Notificaciones.objects.get(id=notif_id)
        notificacion.activa = False
        notificacion.save()

    except:
        pass

    data['notif_actual'] = notificacion

    return render(request, 'panel/notif.html', data)

#CONTENIDOS
##======================================================================
@permission_required('is_superuser')
def crea_edita_contenido(request, tp, ID):
    contenido = None
    contenidos = Contenido.objects.all().order_by('-id')
    msj_nuevo = 'Se creo nuevo post con exito!!!'
    msj_editar = 'Se edito el post con exito!!!'
    msj_eliminar = 'Se elimino el post con exito!!'
    msj_error = 'Error al procesar informacion (%s) :( !!'
    data = dash_card_content(request)

    if ID == 0 and tp == 'nuevo':
            contenido = FormContenido()

    elif ID != 0 and tp == 'editar':
            instancia = Contenido.objects.get(id=ID)
            contenido = FormContenido(instance=instancia)

    elif ID != 0 and tp == 'eliminar':
            instancia = Contenido.objects.get(id=ID)
            instancia.delete()
            messages.warning(request, msj_eliminar)
            return redirect('panel:contenidos', tp='nuevo', ID=0)
    else:
        pass

    if request.method == 'POST':
        if tp == 'editar':
            contenido = FormContenido(request.POST, request.FILES, instance=instancia)
        else:
            contenido = FormContenido(request.POST, request.FILES)
            msj_nuevo = msj_editar

        if contenido.is_valid():
            nuevo = contenido.save(commit=False)
            #post.autor = request.user
            nuevo.fecha_post = timezone.now()
            nuevo.save()
            messages.success(request, msj_editar)
            return redirect('panel:contenidos', tp=tp, ID=ID)
        else:
            print (contenido.errors)
            messages.success(request, msj_error % contenido.errors)
            return redirect('panel:contenidos', tp=tp, ID=ID)
    else:
        data['contenidos'] = contenidos
        data['form'] = contenido
        data['tp'] = tp
        data['Id'] = ID

    return render(request, 'panel/contenidos.html', data)

#TIENDA ======================
@permission_required('is_superuser')
def gestion_tienda(request, tp, ID=None):
    productos = Product.objects.all().order_by('-id')
    contenido = None
    resultado = None
    data = dash_card_content(request)
    msj_nuevo = 'Se creo producto con exito!!!'
    msj_editar = 'Se edito el producto con exito!!!'
    msj_eliminar = 'Se elimino el producto con exito!!'
    msj_error = 'Error al procesar informacion (%s) :( !!'

    if ID is None and tp == 'nuevo':
        contenido = FormProducto()

    elif ID and tp == 'editar':
        instancia = Product.objects.get(id=ID)
        contenido = FormProducto(instance=instancia)

    elif ID and tp == 'ver':
        resultado = Product.objects.get(id=ID)

    elif ID and tp == 'eliminar':
        instancia = Product.objects.get(id=ID)
        instancia.delete()
        messages.warning(request, msj_eliminar)
        return redirect('panel:tienda')
    else:
        pass

    if request.method == 'POST':
        if tp == 'editar':
            contenido = FormProducto(request.POST, request.FILES, instance=instancia)
            msj_nuevo = msj_editar
        else:
            contenido = FormProducto(request.POST, request.FILES)

        if contenido.is_valid():
            nuevo = contenido.save(commit=False)
            #post.autor = request.user
            nuevo.fecha_post = timezone.now()
            nuevo.save()
            messages.success(request, msj_nuevo)
##            return render(request, 'panel/mensaje.html', {'msj':'<h2>Se publico con exito!!</h2>'})
            return redirect('panel:tienda', tp=tp, ID=ID)

        else:
            print (contenido.errors)
            messages.error(request, msj_error % contenido.errors)
            return redirect('panel:tienda', tp=tp, ID=ID)
    else:
        pass

    data['resultados'] = productos
    data['resultado'] = resultado
    data['form'] = contenido
    data['tp'] = tp
    data['Id'] = ID

    return render(request, 'panel/tienda.html', data)


#AVISOS POR EMAIL =======================================
@login_required
@permission_required('is_superuser')
def notificar_x_mail(request, tp, ID):
    correo = None
    mensaje = None
    destinatario = None
    data = dash_card_content(request)

    if tp == 'afiliado':
        afiliado = Cliente.objects.get(id=ID)
        destinatario = afiliado.nombre
        correo = afiliado.datos.correo

    elif tp == 'solicitud':
        solicitud = Solicitud.objects.get(id=ID)
        destinatario = solicitud.nombre
        correo = solicitud.correo

    elif tp == 'usuario':
        usuario = User.objects.get(id=ID)
        destinatario = usuario.username
        correo = usuario.email

    elif tp == 'contacto':
        contacto = Contacto.objects.get(id=ID)
        destinatario = contacto.nombre
        correo = contacto.email

    else:
        pass

    if request.method == 'POST':
        form = FormAviso(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)

            mensaje = """<h2>AVISO</h2>
                    <p>Hola <strong>%s</strong>!!</p>
                    <div id="titulo">%s</div>%s""" % (destinatario, registro.titulo, registro.entrada)

            try:
                mail2 = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(mensaje), EMAIL_HOST_USER, [correo])
                mail2.attach_alternative(plantilla(mensaje), "text/html")
                mail2.send()

                return redirect('/#aviso1', msj='<h2>Aviso enviado con exito!!</h2>')
##                return render(request, 'sitio/mensaje.html', {'msj':'<h2>Aviso enviado con exito!!</h2>'})

            except BadHeaderError:
                return render(request, 'sitio/mensaje.html', {'msj':'<h2>:( Fallo al enviar aviso!!</h2>'})

    else:
        form = FormAviso()
        data['form'] = form
        data['destinatario'] = destinatario


    return render(request, 'panel/aviso_x_mail.html', data)


# BAJA DE AFILIADOS =======================================================================================================================================
@permission_required('is_superuser')
def dar_baja(request, ID):
   solicitud = Solicitud.objects.get(id=ID)
   cliente_aderido = Cliente.objects.get(datos_id=ID)
   if request.method == "GET":
       solicitud.aprobada = False
       solicitud.save()
       cliente_aderido.delete()
       return redirect(request, 'sitio/mensaje.html', {"msj":'<p><h1>Baja de solicitud con exito!!</h1></p>'})

   else:
       pass

   return render(request, 'sitio/mensaje.html', {'msj':'<p><h1>No se pudo dar de baja la solicitud!!</h1></p>'})


def change_info(request):       #Modificar información como visitas al sitio web y visitar ip
    # Por cada visita, agregue 1 al número total de visitas al sitio web
    count_nums = VisitNumber.objects.filter(id=1)
    if count_nums:
        count_nums = count_nums[0]
        count_nums.count += 1
    else:
        count_nums = VisitNumber()
        count_nums.count = 1
    count_nums.save()

    # Registre el número de visitas a ip y cada ip
    if 'HTTP_X_FORWARDED_FOR' in request.META:  # Obtener ip
        client_ip = request.META['HTTP_X_FORWARDED_FOR']
        client_ip = client_ip.split(",")[0]  # Así que aquí está la ip real
    else:
        client_ip = request.META['REMOTE_ADDR']  # Obtenga proxy ip aquí
    # print(client_ip)

    ip_exist = Userip.objects.filter(ip=str(client_ip))
    if ip_exist:  # Determinar si existe la ip
        uobj = ip_exist[0]
        uobj.count += 1
    else:
        uobj = Userip()
        uobj.ip = client_ip
        uobj.count = 1
    uobj.save()

    # Incrementar las visitas de hoy
    date = timezone.now().date()
    today = DayNumber.objects.filter(day=date)
    if today:
        temp = today[0]
        temp.count += 1
    else:
        temp = DayNumber()
        temp.dayTime = date
        temp.count = 1
    temp.save()
