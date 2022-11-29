# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone, dateformat
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import View
from .models import *
from django.db.models import Q
from .forms import *
from PaginaWeb.settings import DATE_INPUT_FORMATS, EMAIL_HOST_USER, TIME_ZONE, NOTIF_EMAIL
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .key_gen import Key
from .msjhtml import plantilla
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from base64 import b64encode
from random import choice, randint
from django.core.files.storage import FileSystemStorage
import time, sys
import mercadopago
from .get_json import Get
from .utils import render2pdf, MPCheckOut
from .mkpdf import CuponPdf
from .proces_xlsx import CargarPlanilla 
import pytz, os, csv

#sys.setdefaultencoding('utf-8')


rango_sorteo = (1500, 5000)

 
# Vista del home
def home(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios").order_by('-id')
    posts_principal = Contenido.objects.filter(categoria__icontains="Principal").order_by('-id')
    posts_lateral = Contenido.objects.filter(categoria__icontains="Lateral")
    notificaciones = Notificaciones.objects.filter(activa=True)
    return render(request, 'sitio/home.html', {'imagenes':servicios, 'principal':posts_principal, 'lateral':posts_lateral, 'notif':notificaciones})

# Vista de busqueda de recibos en base de datos
def pagos_online(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    mp = MPCheckOut(MercadoPagoData.objects.get(nombre="PrevisoraPagos"))
    resultados = {}
    boton_mp = ''
    mensaje = ''
    url_x_afiliado = 'https://www.sysaplicaciones.com.ar/previsora/info.php?clave=prev.753&nroafiliado=%s'
    url_x_dni = 'https://www.sysaplicaciones.com.ar/previsora/info.php?clave=prev.753&nrodni=%s'
    url_respuesta = "https://www.previsoradelnorte.com/clientes/pagos/pago?opcion=%s&monto=%s&recibo=%s"
    num_afiliado = None
    
    if request.method == 'POST':        
        data_input = request.POST['data_num']
        nueva_consulta = Get()
        
        if nueva_consulta.consulta(url_x_afiliado % data_input) or nueva_consulta.consulta(url_x_dni % data_input):
            resultados = nueva_consulta.respuesta
            mp.config(monto=float(resultados[0]['importetotal']), titulo=str(resultados[0]['apellidonombre']))
            mp.respuestas_urls(url_respuesta % (1, float(resultados[0]['importetotal']), resultados[0]['nroafiliado']),
                               url_respuesta % (2, float(resultados[0]['importetotal']), resultados[0]['nroafiliado']),
                               url_respuesta % (3, float(resultados[0]['importetotal']), resultados[0]['nroafiliado']))

            return render(request, 'sitio/pagos_online.html', {'imagenes':servicios,
                                                       'resultados': resultados,
                                                       'msj': mensaje,
                                                       'mp_boton': mp.boton()})

        else:
            mensaje = '<p style="color:red; font-size:10px;">No se encontro datos con el numero ingresado</h2>'
            
    else:
        pass
 
    return render(request, 'sitio/pagos_online.html', {'imagenes':servicios, 'resultados':resultados, 'num_afilado':num_afiliado, 'msj':mensaje})

def cuponpago_pdf(request, ID):
    cupon = Pago.objects.get(id=ID)
    msj = ''
    dir_cupon = ""
    if cupon:
        data = {
                'recibo_n':cupon.recibo_n,
                'monto':cupon.valor,
                'fecha':cupon.fecha,
                'numero':cupon.id,
                'medio':cupon.medio,
            }
        dir_cupon = "/sitio/media/archivos/sitio/doc/cupon%s.pdf" % str(cupon.id)
        pdf = render2pdf('sitio/comprobante.html', data, dir_cupon)
        cupon.comprobante = "archivos/sitio/doc/cupon%s.pdf" % str(cupon.id)
        cupon.save()
        
        return HttpResponse(pdf, content_type='application/pdf')

    else:
        pass
        msj = "<h2>No exite cupon registrado!!!</h2>"
        return render(request, 'sitio/mensaje.html', {'msj':msj})
    
    
    
##@login_required
def cupon_pago(request):
    try:
        monto = request.GET['monto']
        opc = request.GET['opcion']
        recibo = request.GET['recibo']
        
        aviso = """<p><strong>PAGO REALIZADO:</strong> %s</p>
                         <p><strong>Recibo N°:</strong> %s</p>
                         <p><strong>Monto:</strong>$ %s</p>
                         <p><strong>Medio de Pago:</strong>MercadoPago</p>
                         <p><strong>Afiliado N°:<strong>%s</strong></p>
                         """
        
        if opc == '1':
            try:
                registro_pago = Pago()
                registro_pago.recibo_n = int(recibo)
                registro_pago.valor = float(monto)
                registro_pago.forma_pago = 1
##                registro_pago.cliente = "admin"
                registro_pago.save()
                aviso = aviso % (registro_pago.fecha.strftime("%d/%m/%Y %H:%M"), recibo, monto, recibo)
            
                mail1 = EmailMultiAlternatives("AVISO DE PAGO ONLINE: %s" % recibo, aviso, EMAIL_HOST_USER, [EMAIL_HOST_USER, NOTIF_EMAIL])
                mail1.attach_alternative(aviso, "text/html")
                mail1.send()


                mensaje = '''<h2><div id="titulo">MUCHAS GRACIAS POR REALIZAR SU PAGO</div></h2>
                             <p>Recibimos<strong> <h2>$ %s</h2></strong> el <strong>%s</strong> en concepto del pago de cuota, afiliado numero:
                             <strong> %s</strong></p>
                             <p>Estamos procesando el pago, muy pronto impactara en nuestro sistema.</p>
                             <p><a href="/clientes/pagos/recibo/%s"><button>DESCARGAR COMPROBANTE</button></a></p>''' % (monto, registro_pago.fecha.strftime("%d/%m/%Y %H:%M"), recibo, registro_pago.id)

            
            except BadHeaderError:
                mensaje = "<h2>:( Fallo al notificar la operacion!!!</h2>"
                pass
                
        elif opc == '2':
            mensaje = "<h2><strong>:/</strong> La operacion esta pendiente... Por favor espere ser notificado del resultado de la misma.</h2>"
        else:
            mensaje = "<h2>:( La operacion fallo, no se realizo ningun pago!!</h2>"

    except (MultiValueDictKeyError):
        mensaje = "<h2>:( Error al procesar la informacion!!</h2>"
        pass
    
    return render(request, 'sitio/mensaje.html', {'msj': mensaje})

    
# Vista del panel del cliente u usuario        
def panel_cliente(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    return render(request, 'sitio/clientes.html', {'imagenes':servicios})

# Vista de la api de sorteo
@login_required
@permission_required('is_superuser')
def sorteo_api(request):
    cupones = Cupones.objects.all()
    premios = PremiosDeSorteo.objects.all()
    print (premios)
    ganador_iframe = ''
    premio = ''
    entre_todos = None
    contexto = None
    if request.method == 'POST':
        selec = request.POST['premio']
        premio = PremiosDeSorteo.objects.get(nombre=selec)
        try:
            entre_todos = request.POST['x_num_afiliado']
            listas_afiliados = AfiliadosDeSorteo.objects.all()
            
            for db_xlsx in listas_afiliados:
                if db_xlsx.activo:
                    procesar_listas = CargarPlanilla(db_xlsx.archivo.path)
                    eleccion = choice(procesar_listas.buscar_fila('Activo', 2))
                    print (eleccion)
                else:
                    pass
                        
##            print ("Por numero afiliado!!")
##            if Cupones.objects.get(numero_afiliado=eleccion[0]):
##                ganador_iframe = Cupones.objects.get(numero_afiliado=eleccion[0])
##                print (ganador_iframe)
##                
            contexto = {'premio_sorteado':premio,
                        'ganador':eleccion[2],
                        'num_afiliado':int(eleccion[0]),
                        'cupon':None,
                        'total_cupones':cupones.count()}
##            else:
##                pass
        except:
            random_object = cupones[randint(0, cupones.count() - 1)]
            ganador_iframe = random_object
            time.sleep(2)


            contexto = {'premio_sorteado':premio,
                        'ganador':ganador_iframe.nombre,
                        'num_afiliado':ganador_iframe.numero_afiliado,
                        'num_cupon':ganador_iframe.numero_cupon,
                        'cupon':ganador_iframe.comprobante.url,
                        'total_cupones':cupones.count()}
            
        time.sleep(2)
        return render(request, 'sitio/sorteo_api.html', contexto)
    else:
        return render(request, 'sitio/sorteo_api.html', {'premios':premios})


# Funcion que exporta lista a archivo CSV
def exportar_a_csv(request, queryset):

    fecha_y_hora = timezone.now().strftime("%d/%m/%Y %H:%M")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ListaCupones%s.csv"' % fecha_y_hora

    modelo = queryset.model
    modelo_fields = modelo._meta.fields + modelo._meta.many_to_many
    columnas = [field.name for field in modelo_fields]
     
    planilla = csv.writer(response, encoding='utf-8')
    planilla.writerow(columnas)

    filas = queryset.values_list(columnas[0], columnas[1], columnas[2], columnas[3], columnas[4], columnas[5], columnas[6], columnas[7])
    for fila in filas:
        f = []
        for ele in fila:
            if isinstance(ele, str):
                f.append(ele.encode("UTF-8"))
            else:
                f.append(ele)
            
        planilla.writerow(f, encoding='utf-8')

    return response


# Vista u opcion de descarga grilla o lista
def descargar_csv(request):
    busqueda = request.GET['data']
    if busqueda == "todos":
        cupones = Cupones.objects.all()
    else:
        filtros = (Q(nombre__icontains=busqueda) |
                    Q(correo__icontains=busqueda) |
                    Q(numero_afiliado__icontains=busqueda) |
                    Q(numero_cupon__icontains=busqueda) | 
                    Q(telefono__icontains=busqueda) |
                    Q(usuario__username__icontains=busqueda)
                   )
        
        cupones = Cupones.objects.filter(filtros)
        
    return exportar_a_csv(request, cupones)


@login_required
@permission_required('is_superuser')
def listar_usuarios(requets):
    usuarios = User.objects.all()
    return render(requets, 'sitio/usuarios.html', {'usuarios':usuarios})


@login_required
@permission_required('is_superuser')
def ver_mensajes(request):
    contacto = Contacto.objects.all()
    return render(request, 'sitio/consulta-msj.html', {'mensajes':contacto})

@login_required
def buscar(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    resultados = []
    clientes = eval(request.GET.get('cli'))
    if request.method == "POST":
        busqueda = request.POST['entrada']
        if clientes:
            if busqueda == "todos":
                resultados = Cliente.objects.all()
            else:
                querys = (Q(datos__id__icontains=busqueda) |
                  Q(datos__dni__icontains=busqueda) |
                  Q(datos__nombre__icontains=busqueda) |
                  Q(datos__apellido__icontains=busqueda) |
                  Q(datos__correo__icontains=busqueda) |
                  Q(usuario__username__icontains=busqueda)
                )
                resultados = Cliente.objects.filter(querys)
                
        else:
            if busqueda == "todos":
                resultados = User.objects.all()
            else:
                querys = (Q(id__icontains=busqueda) |
                  Q(username__icontains=busqueda) |
                  Q(email__icontains=busqueda)
                )

                resultados = User.objects.filter(querys)
                       
        
    return render(request, 'sitio/buscar.html', {'dbclientes':clientes, 'resultados':resultados, "imagenes":servicios})

@login_required
def consulta_x_dni(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    if request.method == "POST":
        dni_ingresado = request.POST['dni']
        print (dni_ingresado)
        try:
            busqueda = Solicitud.objects.get(dni=dni_ingresado)
            
        except Solicitud.DoesNotExist:
            pass
            busqueda = False
    else:
        pass
        busqueda = False


    return render(request, 'sitio/consulta-cliente.html', {'resultado':busqueda, "imagenes":servicios})

@login_required
def consulta_cupones(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    
    if request.method == "POST":
        busqueda = request.POST['entrada']
        
        if busqueda == "todos":
            cupones = Cupones.objects.all()
        else:
            if str(busqueda).isdigit():
                filtros = (
                            Q(numero_afiliado=busqueda) |
                            Q(numero_cupon=busqueda) | 
                            Q(telefono=busqueda)
                            )
            else:
                filtros = (Q(nombre__icontains=busqueda) |
                      Q(correo__icontains=busqueda) |
                      Q(usuario__username__icontains=busqueda)
                     )
                
            try:
                cupones = Cupones.objects.all().filter(filtros)
            except Cupones.DoesNotExist:
                pass
                cupones = False

        return render(request, 'sitio/consulta-cupones.html', {'resultados':cupones, "imagenes":servicios, "data":busqueda})
    
    else:
        cupones = Cupones.objects.all()

    return render(request, 'sitio/consulta-cupones.html', {'resultados':cupones, "imagenes":servicios, "data":'todos'})


@login_required
def asociar_a_usuario(request, ID):
    respuesta = """<h2>ASOCIASTE AFILIADO A TU CUENTA!</h2>
                   <p>Hola %s, has asociado al afiliado <strong>%s %s</strong> a tu cuenta de usuario,</p>
                   <p>desde ahora podras gestionar su afiliacion y ver su cupon de pagos junto a las tuyas.</p>
                   <p>Ante cualquier duda comunicate con nosotros, estamos para asistirte.</p>
                    <a href="www.previsoradelnorte.com/contacto/">
                    <button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">CONSULTAS</button></a>
                   """

    notificar = """<h2>ASOCIO AFILIADO/CLIENTE A USUARIO</h2>
                 <p>Usuario: %s</p>
                 <p>Afiliado: %s %s</p>
                 <p>Fecha: %s</p>"""
    
    if request.method == "GET":
        try:
            
            cliente = Cliente.objects.get(datos__id=ID)
            cliente.usuario = request.user
            cliente.save()

            respuesta = respuesta % (request.user.username, cliente.datos.nombre, cliente.datos.apellido)
            notificar = notificar % (request.user.username, cliente.datos.nombre, cliente.datos.apellido, timezone.now().strftime("%d/%m/%Y %H:%M"))

            if request.user.is_superuser:
                pass

            else:
                mail = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), EMAIL_HOST_USER, [request.user.email])
                mail.attach_alternative(plantilla(respuesta), "text/html")
                mail.send()

                mail2 = EmailMultiAlternatives("AVISO DE USUARIO: %s" % request.user.username, notificar, [request.user.email], [EMAIL_HOST_USER, NOTIF_EMAIL])
                mail2.attach_alternative(notificar, "text/html")
                mail2.send()
            
            return render(request, 'sitio/mensaje.html', {'msj':"<h2>Asociaste al afliado <strong>%s %s</strong> a tu cuenta con exito!!!</h2>" % (cliente.datos.nombre, cliente.datos.apellido)})

            
        except Cliente.DoesNotExist:
            pass

            return render(request, 'sitio/mensaje.html', {'msj':"<h2>No se pudo asociar al afiliado a tu cuenta de usuario!!!</h2>"})

@login_required
@permission_required('is_superuser')
def ver_afiliado(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    solicitudes = []
    if request.method == "POST":
        busqueda = request.POST['entrada']
        if busqueda == "todos":
            solicitudes = Solicitud.objects.all()
        else:
            querys = (Q(id__icontains=busqueda) |
                Q(dni__icontains=busqueda) |
                Q(nombre__icontains=busqueda) |
                Q(correo__icontains=busqueda) |
                Q(usuario__username__icontains=busqueda)
                )
            
            solicitudes = Solicitud.objects.filter(querys)
            

    return render(request, 'sitio/alta.html', {'resultados':solicitudes, "imagenes":servicios})


@login_required
@permission_required('is_superuser')
def dar_alta(request, ID):
    solicitud = Solicitud.objects.get(id=ID)
    cliente_nuevo = FormCliente()
    if request.method == "POST":
        cliente_nuevo = FormCliente(data=request.POST)
        if cliente_nuevo.is_valid:
            cliente_nuevo.save(commit=False)
            solicitud.aprobada = True
            solicitud.save()
            cliente_nuevo.save()
        

            respuesta = """<h2>SOLICITUD APROBADA!</h2>
                            <p>Hola <strong>%s %s</strong>!!</p>
                            <p>Te informamos que la <strong>Solicitud de Afiliación</strong> ha sido aprobada!!</p>
                            <p>A partir de la siguiente fecha <strong>%s</strong> eres afiliado de la previsora y el plazo de carencia es de <strong>%s</strong> meses a partir de la fecha de afiliación.</p>
                            <p>Recuerda realizar el abono de tu cuota que es de: <strong><h2>$%s</h2></strong> todos los meses sin recargos hasta el dia 10 inclusive; podes utilizar los siguientes medios de pagos:<br><strong>Efectivo / Débito / Crédito / Mercado Pago</strong></p>
                            <p>Tu cuenta esta activa en el sitio web de la previsora, ingresando contaras con opciones de autogestion en la opción de menú <strong>"CLIENTES"</strong>.</p>
                            
                            <a href="www.previsoradelnorte.com"><button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">IR AL SITIO</button></a>
                             """ % (solicitud.nombre.upper(), solicitud.apellido.upper(), solicitud.fecha.strftime("%d/%m/%Y %H:%M"), solicitud.plan.vigencia, solicitud.plan.valor)

            print (solicitud.correo)
            if solicitud.correo is None:
                pass
                return render(request, 'sitio/mensaje.html', {"msj":"<h2>Se ha dado el alta al cliente <strong>%s</strong></h2>" % solicitud.nombre.upper})
    
            else:
                try:
                    mail = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), EMAIL_HOST_USER, [solicitud.usuario.email])
                    mail.attach_alternative(plantilla(respuesta), "text/html")
                    mail.send()
                
                    return render(request, 'sitio/mensaje.html', {"msj":"<h2>Se ha dado el alta al cliente <strong>%s</strong></h2>" % solicitud.usuario.username})
                
                except ValueError:
                    pass
                    return render(request, 'sitio/mensaje.html', {"msj":"<h2>Fallo al notificar el alta!</h2>"})

    else:
        default = {"numero":Cliente.objects.all().count() + 1,
                   "usuario":solicitud.usuario,
                   "datos":solicitud,
                   "activo":True,
                   "monto":solicitud.plan.valor}
        
        cliente_nuevo = FormCliente(initial=default)
        

    return render(request, 'sitio/prev_alta.html', {"form": cliente_nuevo})


@login_required
@permission_required('is_superuser')
def dar_baja(request, ID):
    solicitud = Solicitud.objects.get(id=ID)
    cliente_aderido = Cliente.objects.get(datos_id=ID)
    if request.method == "GET":
        solicitud.aprobada = False
        solicitud.save()
        cliente_aderido.delete()
        return render(request, 'sitio/mensaje.html', {"msj":'<p><h1>Baja de solicitud con exito!!</h1></p>'})

    else:
        pass

    return render(request, 'sitio/mensaje.html', {'msj':'<p><h1>No se pudo dar de baja la solicitud!!</h1></p>'})
        
        
            
def ver_planes(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    planes = Plan.objects.all()
    return render(request, 'sitio/planes.html', {"planes":planes, "imagenes":servicios})


class FakePost():
    def __init__(self):
        self.titulo = False
        self.autor = False
        self.categoria = False
        self.imagen = False
        self.texto = False
        self.fecha_post = None
        self.id = 0
        

@login_required
@permission_required('is_superuser')
def pre_contenido(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    if request.method == "POST":
        post = FakePost()
        post.titulo = request.POST.get('titulo')
        post.autor = request.user.username
        if request.FILES.get('imagen', False):
            encoded = b64encode(request.FILES.get('imagen').read())
            mime = "image/png"
            mime = mime + ";" if mime else ";"
            post.imagen = {"url":"data:%sbase64,%s" % (mime, encoded)}
            print (post.imagen)
        
        post.categoria = request.POST.get('categoria')
        post.fecha_post = timezone.now
        post.texto = request.POST.get('texto')


        
        return render(request, 'sitio/ver.html', {'posteos':[post], 'titulos':"Vista Previa: " + post.titulo, 'imagenes':servicios, 'fecha':timezone.now})


def mostrar_contenido(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    notificaciones = Notificaciones.objects.filter(activa=True)
    busqueda = request.GET.get('search', '')
    querys = (Q(categoria__icontains=busqueda) |
              Q(titulo__icontains=busqueda) |
              Q(id__icontains=busqueda)
             )
    if busqueda == "todas":
        post = Contenido.objects.all().order_by('-fecha_post')
    else:
        post = Contenido.objects.filter(querys).order_by('-fecha_post')
        
    return render(request, 'sitio/ver.html', {'posteos':post, 'titulos':busqueda, 'imagenes':servicios, 'notif':notificaciones})


@login_required
@permission_required('is_superuser')
def mostrar_notif(request, ID):
    notificaciones = Notificaciones.objects.get(id=ID)
    notificaciones.activa = False
    notificaciones.save()
        
    return render(request, 'sitio/mensaje.html', {'msj':notificaciones.mensaje})

def calcular_plan(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    plan_encontrado = None
    fecha_hoy = datetime.now()
    plantilla = None
    fecha_inicio = None
    valor_total = None
    valor_descon = None
    titulo = None
    plan_id = None

    if request.method == 'POST':
        try:
            entrada = int(request.POST.get('edad', ''))
            planes = Plan.objects.all()
            for plan in planes:
                edades = list(range(eval(plan.periodo)[0], eval(plan.periodo)[1] + 1))
                if entrada in edades:
                    plan_encontrado = plan

            fecha_inicio = fecha_hoy + relativedelta(months=plan_encontrado.vigencia)
            valor_descon = plan_encontrado.valor - plan_encontrado.valor * plan_encontrado.descuento / 100
            valor_total = plan_encontrado.valor
            titulo = plan_encontrado.titulo
            plan_id = plan_encontrado.id

            plantilla = """
                    <p>Con un plazo de carencia de <strong>%s meses</strong>, y a partir de la fecha de hoy <strong>%s</strong> la cobertura entraría en vigencia a partir del <strong>%s</strong>.<p>
                    <p>La cobertura de este plan cuenta con los siguientes elementos:</p><p><strong>%s</strong></p><p style="font-size:10px;">prestadora de servicios<br><a href="/sanfrancisco/">COCHERIA SAN FRANCISCO</a></p>
                    <p>El valor nominal de la cuota a abonar sera de <h1 style="color:#728e3a; text-shadow: 1px 1px white;">$%s</h1><p style="font-size:10px;">Medios de pagos:  <strong>Débito / Crédito / Efectivo</strong></p><p>sujeto a actualizaciones de acuerdo a lo establecido en un contrato legal.<p>
                    <p>Realizando su solicitud desde aquí sera beneficiado con un descuento del <h1 style="color:#728e3a; text-shadow: 1px 1px white;">%s&#37;</h1> en el valor de la cuota; Así como también si adherís tu solicitud y las de otras <strong>3 personas</strong> mas a tu cuenta, recibirás un descuento del <h1 style="color:#728e3a;">%s&#37;</h1>
                    <p>Para completar el formulario de afiliación haz click en el siguiente botón.</p>
                    """ % (plan_encontrado.vigencia, fecha_hoy.strftime("%d/%m/%Y"), fecha_inicio.strftime("%d/%m/%Y"), plan_encontrado.descrip, valor_total, plan_encontrado.descuento, plan_encontrado.descuento_grupo) 
               
        except ValueError:
            plan_encontrado = False
        ##return render(request, 'sitio/planes.html', {'plan':plan_encontrado})


    return render(request, 'sitio/calculadora.html', {'plan':plantilla, 'titulo':titulo, 'imagenes':servicios, 'plan_id':plan_id})

##vista de participacion
def registro_al_sorteo(request):
    resultados = {}
    numeros_asignados = []
    numero_selec = ""
    mensaje = ""
    cupones_solicitados = ''
    url_x_afiliado = 'https://www.sysaplicaciones.com.ar/previsora/info.php?clave=prev.753&nroafiliado=%s'
    url_x_dni = 'https://www.sysaplicaciones.com.ar/previsora/info.php?clave=prev.753&nrodni=%s'
    formulario = []
    default = {}
    cupones_solicitados = Cupones.objects.all()
    if cupones_solicitados:
        for cupon in cupones_solicitados:
            numeros_asignados.append(cupon.numero_cupon)
            numero_selec = choice([i for i in range(rango_sorteo[0],rango_sorteo[1]) if i not in numeros_asignados])

    else:
        numero_selec = choice([i for i in range(rango_sorteo[0],rango_sorteo[1])])
            
    if request.method == "POST":
        formulario = FormCupon()
        data_input = request.POST['data']
        nueva_consulta = Get()
        if request.user.is_superuser:
            pass

        else:
            try:
                if nueva_consulta.consulta(url_x_afiliado % data_input) or nueva_consulta.consulta(url_x_dni % data_input):
                    resultados = nueva_consulta.respuesta
                    print (resultados)
                    default = {
                                 'nombre':str(resultados[0]['apellidonombre']),
                                 'dni':str(resultados[0]['nrodocumento']),
                                 'numero_afiliado':str(resultados[0]['nroafiliado']),
                                 'numero_cupon':numero_selec,
                               }
                    formulario = FormCupon(initial=default)
                                
                    

                else:
                    mensaje = '<p style="color:red; font-size:11px;">No se encontro afiliado activo con ese dato ingresado</p>'

            except AfiliadosDeSorteo.DoesNotExist:
                mensaje = '<p style="color:red; font-size:10px;">No exite afiliados en la base de datos, vueva intentarlo en otra ocasion.</p>'
                pass
    else:   
        if request.user.is_superuser:
            default = {
                        'numero_cupon':numero_selec,
                        'usuario':request.user,
                      }
            formulario = FormCupon(initial=default)
        else:
            
            pass

    return render(request, 'sitio/registro_sorteo.html',
                  {'resultado':resultados, 'msj':mensaje, 'form_cupon':formulario, 'rangoi':rango_sorteo[0], 'rangof':rango_sorteo[1], 'total_cupon':cupones_solicitados})


##Vista de Sorteo
def cupon_sorteo(request):
    numeros_asignados = []
    numero_selec = None
    cupones = Cupones.objects.all()
    post_premios = Contenido.objects.filter(titulo__icontains="PREMIOS")
    post_bases = Contenido.objects.filter(titulo__icontains="REQUISITOS")
    aviso = """<p><strong>Nombre y Apellido:</strong> %s</p>
               <p><strong>Numero de Afiliado:</strong> %s</p>
               <p><strong>Correo:</strong> %s</p>
               <p><strong>Fecha:</strong> %s</p>
            """
    respuesta = """<h2>YA ESTAS PARTICIPANDO!</h2>
                    <p>Hola <strong>%s</strong>!!</p>
                    <p>Te informamos que tu cupón digital N°: <h2>%s</h2> del <strong>GRAN SORTEO JUNIO 2022</strong> se registro con éxito!!</p>
                    <p>EL sorteo se llevara a cabo  el día <strong>SABADO 25 JUNIO DEL 2022</strong>, el único requisito es estar día con tus cuotas y seras aprobado sin inconvenientes, de lo contrario puedes aprovechar para ponerte al día previo al sorteo.</p>
                    <p>Participaras por los siguientes premios:<br><br><strong>1° Premio  - Smart TV de 32 pulgadas.<br>2° Premio - Termo Mate/Tereré 1L.<br>3° Premio - Jarra Electrica 2L.<br>4° Premio - Plancha Automática.</strong></p>
                    <p>Puedes descargar tu <strong>cupón comprobante</strong> en formato <strong>PDF</strong> haciendo click en el siguiente botón.</p>
                    <p><h2>MUCHA SUERTE!</h2></p>
                    <p><a href="www.previsoradelnorte.com/%s"><button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">DESCARGAR CUPON</button></a>
                """
    mensaje_ok = """<p><h3>GENIAL!!!</h3></p><p>YA ESTAS PARTICIPANDO DEL <strong>GRAN SORTEO JUNIO 2022</strong></p><p>UN AVISO SE TE ENVIARA AL CORREO ELECTRONICO O A TU CELULAR.</p>
                    <iframe src="/media/%s#toolbar=0" width="100%%" height="500px"></iframe>
                    <p><a href="/media/%s" target="_blank" download><button class="custom-boton">DESCARGAR COMPROBANTE</button></a></p>"""

    mensaje_ko = """<p><h2 style="color:red;">AVISO !!</h2></p><h1>%s</h1><p><h3>USTED YA REGISTRO UN CUPON DEL SORTEO.</h3></p><p><a href='%s'><button class="custom-boton">VER COMPROBANTE</button></a></p>"""
    
    if request.method == "POST":
        instancia = FormCupon(data=request.POST)
        if instancia.is_valid():
            form_cupon = instancia.save(commit=False)
            print (form_cupon.numero_cupon)
            filtros = (
                       Q(numero_cupon=form_cupon.numero_afiliado) |
                       Q(nombre=form_cupon.nombre) 
                      )

            #Filtra los datos ingresados en caso de coincidir con algun cupon
            if Cupones.objects.filter(filtros):
                cupon_generado = Cupones.objects.get(nombre=form_cupon.nombre)
                return render(request, 'sitio/mensaje.html', {'msj':mensaje_ko % (cupon_generado.nombre, cupon_generado.comprobante.url)})

            elif Cupones.objects.filter(numero_cupon=form_cupon.numero_cupon):
                mensaje_ko = '''<p><h2 style="color:red;">AVISO !!</h2></p><h1>%s</h1><p><h3>YA SE REGISTRO UN CUPON CON EL MISMO NUMERO.</h3></p>'''
                return render(request, 'sitio/mensaje.html', {'msj':mensaje_ko % (form_cupon.numero_cupon)})
                
            else:
                ##
                if request.user.is_authenticated:
                    form_cupon.usuario = request.user
                else:
                    pass
                    
                ###ACA VAN LOS AVISOS
                aviso = aviso % (form_cupon.nombre, form_cupon.numero_afiliado, form_cupon.correo, form_cupon.fecha.strftime("%d/%m/%Y %H:%M"))
                if request.user.is_superuser:
                    form_cupon.verificado = True
                    pass
                else:
                    try:
                        mail_a_previsora = EmailMultiAlternatives("NUEVO CUPON DE SORTEO: %s" % form_cupon.numero_cupon, aviso, form_cupon.correo, [EMAIL_HOST_USER, NOTIF_EMAIL])
                        mail_a_previsora.attach_alternative(aviso, "text/html")
                        mail_a_previsora.send()

                        if form_cupon.correo:
                            respuesta = respuesta % (form_cupon.nombre, form_cupon.numero_cupon, "media/archivos/sitio/doc/cupon%s.pdf" % form_cupon.numero_cupon)
                            mail_a_afiliado = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), EMAIL_HOST_USER, [form_cupon.correo])
                            mail_a_afiliado.attach_alternative(plantilla(respuesta), "text/html")
                            mail_a_afiliado.send()
                        else:
                            pass

                    except ValueError:
                        pass

                #GENERA EL COMPROBANTE EN PDF
                cupon_pdf = CuponPdf(str(form_cupon.numero_cupon), form_cupon.nombre.upper(), str(form_cupon.numero_afiliado), timezone.now().strftime("%d/%m/%Y %H:%M"), len(form_cupon.nombre))
                cupon_pdf.output(os.getcwd() + '/sitio/media/archivos/sitio/doc/cupon%s.pdf' % form_cupon.numero_cupon, 'F')
                form_cupon.comprobante = "archivos/sitio/doc/cupon%s.pdf" % form_cupon.numero_cupon
                form_cupon.save()
                mensaje_ok = mensaje_ok % (form_cupon.comprobante, form_cupon.comprobante)
                
                return render(request, 'sitio/mensaje.html', {'msj':mensaje_ok})

        else:
            pass
            print (instancia.errors)
            return render(request, 'sitio/mensaje.html', {'msj':"""<h2 style="color:red;"><p>ERROR AL PROCESAR SU CUPON!</p><p>%s</p>%s</h2>""" % (instancia.errors, '''<a href="{% url 'sorteo' %}"><button class="custom-boton">VOLVER</button></a>''')})

    else:
        #Determina si hay cupones ya asociados
        if cupones:
            for cupon in cupones:
                numeros_asignados.append(cupon.numero_cupon)

            numero_selec = choice([i for i in range(rango_sorteo[0],rango_sorteo[1]) if i not in numeros_asignados])

        else:
            numero_selec = choice([i for i in range(rango_sorteo[0],rango_sorteo[1])])

        #Formulario que muestra el numero seleccionado al azar
        default = {'numero_cupon': numero_selec}
        form = FormCupon(initial=default)
        
    return render(request, "sitio/cupon_sorteo.html", {'form_cupon':form, 'post_bases':post_bases, 'post_premios':post_premios, 'rangoi':rango_sorteo[0], 'rangof':rango_sorteo[1], 'total_cupon':cupones})

def vista_contacto(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    contacto = ContactoForm()
    aviso = """<p><strong>CONSULTA DE:</strong></p>
                         <p><strong>Nombre y Apellido:</strong> %s</p>
                         <p><strong>Numero de Teléfono:</strong> %s</p>
                         <p><strong>Correo:</strong> %s</p>
                         <textarea style='widht:200px;'>%s</textarea>"""
    
    mensaje = '<div id="titulo">MENSAJE ENVIADO!</div><p><h3>Gracias por contactarnos, hemos recibido tu mensaje con éxito y recibirás una respuesta muy pronto.</h3></p>'
    if request.method == 'POST':
        contacto = ContactoForm(data=request.POST or None)
        if contacto.is_valid:
            registro = Contacto()
            subject = request.POST['Nombre']
            from_email = request.POST['Correo']
            telef = request.POST['Telefono']
            message = request.POST['Mensaje']
            registro.nombre = subject
            registro.email = from_email
            registro.numero = telef
            registro.texto = message
            aviso = aviso % (subject, telef, from_email, message)
            try:
                mail = EmailMultiAlternatives("MENSAJE DE CONTACTO: %s" % timezone.now().strftime("%d/%m/%Y %H:%M"), aviso, from_email, [EMAIL_HOST_USER, NOTIF_EMAIL])
                mail.attach_alternative(aviso, "text/html")
                mail.send()
                registro.save()
                
                #send_mail(subject, message, from_email, ['contacto@cocheriasanfrancisco.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
            return render(request, 'sitio/mensaje.html', {'msj':mensaje})
        

    return render(request, "sitio/contacto.html", {'form':contacto, 'imagenes':servicios})

def solicitar_baja(request):
    if request.method == "POST":
        solicitudes = request.POST.getlist('solicitudes')
        pass

    else:
        pass


    return render(request, 'sitio/')

@login_required    
def vista_solicitud(request):
    es_cliente = False
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    mensaje = '<div id="titulo">PERFECTO!!</div><p>Gracias por enviar tu solicitud, revisa tu correo electronico para confirmar tu peticion.</p>'
    if request.method == 'POST':
        peticion = FormSolicitud(data=request.POST)
        if peticion.is_valid():
            cliente_nuevo = peticion.save(commit=False)
            clave = Key(5)
            cliente_nuevo.validacion = clave
            cliente_nuevo.usuario = request.user
            #cliente_nuevo.fecha = timezone.now()
            cliente_nuevo.save()
            message = """<p><strong>SOLICITUD DE AFILIACIÓN:</strong> %s</p>
                         <p><strong>Nombre y Apellido:</strong> %s %s</p>
                         <p><strong>Numero de Documento:</strong> %s</p>
                         <p><strong>Numero de Teléfono:</strong> %s</p>
                         <p><strong>Correo:</strong> %s</p>
                         """ % (timezone.now().strftime("%d/%m/%Y %H:%M"), request.POST['nombre'], request.POST['apellido'], request.POST['dni'], request.POST['telefono'], request.POST['correo'])
            
            respuesta = """<h2>SOLICITUD REGISTRADA!</h2></div> 
                                <p>Hola <strong>%s %s</strong>!!</p>
                                <p>Gracias por confiar en nosotros, tu <strong>Solicitud de Afiliación</strong> se registro con éxito.</p>
                                <p>Un representante de <strong>LA PREVISORA DEL NORTE</strong> se pondra en contacto con usted, para dar el alta a su afilicación.</p>
                                <p>Ultimo paso, para confirmar y verificar su petición, por favor haz click en el siguiente botón.</p>
                                <a href="https://www.previsoradelnorte.com/clientes/validar/?clave=%s">
                                <button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">CONFIRMA TU SOLICITUD</button></a>
                             """ % (request.POST['nombre'].upper(), request.POST['apellido'].upper(), clave)
            
            if request.user.is_superuser:
                pass
                #return render(request, 'sitio/mensaje.html', {'msj':"<h2>Solicitud cargada con exito!!</h2>"})
                return redirect("/admin/solicitudes/alta/%s/" % cliente_nuevo.id)

            else:
                try:
                    mail = EmailMultiAlternatives("SOLICITUD DE AFILIACION: %s" % request.POST['dni'], message, request.POST['correo'], [EMAIL_HOST_USER, NOTIF_EMAIL])
                    mail.attach_alternative(message, "text/html")
                    mail.send()
                
                    mail2 = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), EMAIL_HOST_USER, [request.POST['correo']])
                    mail2.attach_alternative(plantilla(respuesta), "text/html")
                    mail2.send()
            
                    return render(request, 'sitio/mensaje.html', {'msj':mensaje})
                
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
    
        else:
            print (peticion.errors)
    else:
        plan_id = request.GET.get('plan')
        usuario = User.objects.get(username=request.user.username)
        if eval(plan_id):
            plan = Plan.objects.get(id=plan_id)
            default = {'correo': usuario.email, 'plan': plan}
            peticion = FormSolicitud(initial=default)

        else:
            if request.user.is_superuser:
                default = {'usuario': usuario}
                peticion = FormSolicitud(initial=default)
            else:
                default = {'correo': usuario.email}
                peticion = FormSolicitud(initial=default)
                

    return render(request, "sitio/solicitud.html", {'form':peticion, 'imagenes':servicios, 'es_cliente':es_cliente})

def validar(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    registrado = None
    
    if request.method == "GET":
        if request.GET.get('clave', ''):
            try:
                solicitud = Solicitud.objects.get(validacion=request.GET.get('clave'))
                solicitud.verificado = True
                solicitud.save()
                registrado = solicitud.nombre
                mensaje = """<h2><p><strong>%s</strong> tu solicitud ha sido verificada!!</p></h2>
                            <p>Muy pronto representantes de la Previsora se pondrán en contacto con usted.</p>
                            <a href="/"><button class="custom-boton">VOLVER</button></a>""" % registrado

                return render(request, 'sitio/mensaje.html', {'msj':mensaje})
            except Solicitud.DoesNotExist:
                pass
                    
        elif request.GET.get('email', ''):
            try:
                usuario = User.objects.get(email=request.GET.get('email'))
                instancia = PerfilUsuario.objects.get(usuario=usuario)


                registrado = usuario.username    
                mensaje = """<h2><p><strong>%s</strong> tu registro ha sido un exito!!</p></h2>
                            <p>Para ingresar a tu cuenta solo dale un click al siguiente botón.</p>
                            <a href="%s"><button class="custom-boton">INGRESAR</button></a>""" % (registrado, '''{% url 'login' %}''')

                form = FormPerfil(instance=instancia)
            
                return render(request, 'sitio/validar_registro.html', {'form':form, 'imagenes':servicios, 'usuario':usuario})
            
            except (User.DoesNotExist, PerfilUsuario.DoesNotExist):
                pass
                
    elif request.method == "POST":
        busqueda = User.objects.get(email=request.GET.get('email'))
        instancia = PerfilUsuario.objects.get(usuario=busqueda)
        form = FormPerfil(request.POST, instance=instancia)
        
        if form.is_valid():
            datos = form.save(commit=False)
            datos.usuario = busqueda
            busqueda.is_active = True
            busqueda.save()
            datos.save()

            return redirect("/clientes/validar/?email=%s" % busqueda.email)
        
        else:
            print (form.errors)
            
            
    return render(request, 'sitio/mensaje.html', {'msj':'<div id="titulo">OOPS!!</div><p><h2>La validacion Fallo!!</h2></p>', "imagenes":servicios})

def recuperar_pass(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    clave_provi = None
    encontrado = None
    if request.method == "POST":
        ingresado = request.POST['correo_recuperacion']
        try:
            usuario = User.objects.get(email=ingresado)
            clave_provi = Key(8)
            usuario.password = make_password(clave_provi)
            encontrado = usuario.username
            usuario.is_active = False
            usuario.save()
            respuesta = """<h2>RECUPERACION DE CLAVE</h2>
                            <p>Hola <strong>%s</strong>!!</p>
                            <p>Tu solicitud de recuperacion de clave ha sido un éxito.</p>
                            <p>Esta es tu nueva clave provisoria: <strong><h3>%s</h3></strong>. Por favor toma nota y haz click en el boton de abajo para validar tu cuenta.</p>
                            <a href="https://www.previsoradelnorte.com/clientes/validar/?email=%s">
                            <button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">VALIDAR</button></a>
                        """ % (encontrado, clave_provi, ingresado)


            mail = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), "contacto@cocheriasanfrancisco.com", [ingresado])
            mail.attach_alternative(plantilla(respuesta), "text/html")
            mail.send()

        except User.DoesNotExist:
            return render(request, 'sitio/mensaje.html', {msj:'<h2><strong>Error!!!</strong> el correo ingresado no pertenece a un usuario registrado</h2>', "imagenes":servicios})
    else:
        pass    

    return render(request, 'sitio/recuperacion.html', {'usuario':encontrado, "imagenes":servicios})
                  
@login_required
def nuevo_contenido(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    if request.method == 'POST':
        contenido = FormContenido(request.POST, request.FILES)
        if contenido.is_valid():
            nuevo = contenido.save(commit=False)
            #post.autor = request.user
            nuevo.fecha_post = timezone.now()
            nuevo.save()
            return render(request, 'sitio/mensaje.html', {'msj':'<h2>Se publico con exito!!</h2>', "imagenes":servicios})
        else:
            print (contenido.errors)
            return render(request, 'sitio/mensaje.html', {'msj':'<h2>Error!! no se pudo publicar..</h2>', "imagenes":servicios})
    else:
        contenido = FormContenido()

    return render(request, 'sitio/publicar.html', {'form':contenido, "imagenes":servicios})



@login_required
@permission_required('is_superuser')
def enviar_aviso(request, ID):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    cliente = request.GET.get('cli')
    correo = None
    mensaje = None
    destinatario = None
    if request.method == 'POST':
        if eval(cliente):
            usuario = Solicitud.objects.get(id=ID)
            correo = usuario.correo
            destinatario = "%s %s" % (usuario.nombre, usuario.apellido)
        else:
            usuario = User.objects.get(id=ID)
            correo = usuario.email
            destinatario = usuario.username

        form = FormAviso(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)

            mensaje = """<h1>AVISO</h1>
                    <p>Hola <strong>%s</strong>!!</p>
                    <div id="titulo">%s</div>%s""" % (destinatario, registro.titulo, registro.entrada)
 
            try:
                mail2 = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(mensaje), EMAIL_HOST_USER, [correo])
                mail2.attach_alternative(plantilla(mensaje), "text/html")
                mail2.send()
                
                return render(request, 'sitio/mensaje.html', {'msj':'<h2>Aviso enviado con exito!!</h2>'})

            except BadHeaderError:
                return render(request, 'sitio/mensaje.html', {'msj':'<h2>:( Fallo al enviar aviso!!</h2>'})

    else:
        if eval(cliente):
            usuario = Solicitud.objects.get(id=ID).correo
        else:
            usuario = User.objects.get(id=ID).email
            
        form = FormAviso()


    return render(request, 'sitio/aviso.html', {'form':form, 'destinatario':usuario, "imagenes":servicios})
            
            
def vista_registro(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    if request.method == 'POST':
        form = FormRegistro(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            message = """<p><strong>FECHA DE REGISTRO:</strong> %s</p>
                         <p><strong>USUARIO:</strong> %s</p>
                         <p><strong>PASSWORD:</strong> %s</p>
                         <p><strong>CORREO:</strong> %s</p>""" % (timezone.now(), request.POST['username'], request.POST['password1'], request.POST['email'])
            
            respuesta = """<h2>COMPLETA TU REGISTRO!</h2> 
                                <p>Hola <strong>%s</strong>!!</p>
                                <p>Gracias por registrarte a nuestro sitio web, recordá que tu contraseña es: <strong>%s</strong> .</p>
                                <p>Este es el ultimo paso para habilitar tu registro, por favor haz click en el siguiente botón y completa algunos datos.</p>
                                <a href="https://www.previsoradelnorte.com/clientes/validar/?email=%s">
                                <button style="background: #728e3a;color: white;padding: 10px;font-size: 18px;border-radius: 5px;">CONFIRMA TU REGISTRO</button>
                                </a>""" % (usuario.username, request.POST['password1'], usuario.email.lower())
            
            try:
                mail = EmailMultiAlternatives("SOLICITUD DE REGISTRO: %s" % usuario.username, message, usuario.email.lower(), [EMAIL_HOST_USER, NOTIF_EMAIL])
                mail.attach_alternative(message, "text/html")
                mail.send()
                
                mail2 = EmailMultiAlternatives("PREVISORA DEL NORTE", plantilla(respuesta), EMAIL_HOST_USER, [usuario.email.lower()])
                mail2.attach_alternative(plantilla(respuesta), "text/html")
                mail2.send()

                usuario.is_active = False
                usuario.save()
                
                return render(request, 'sitio/mensaje.html', {'msj':'<div id="titulo">PERFECTO!</div><p><h2>Revisa tu correo electronico, econtraras un email con el enlace para validar tu registro.</h2></p>'})

                
            except  BadHeaderError:
                return render(request, 'sitio/mensaje.html', {'msj':'<p><h1>OOPS!! :(</h1><p><p>Hubo un error con tu direccion de correos revisa si es valida!!</p>'})
                
    else:
        
        form = FormRegistro()

    return render(request, "sitio/registro.html", {'form': form, 'imagenes':servicios})


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
            return render(request, 'sitio/mensaje.html', {'msj':'<h2>Post editado con exito!!</h2>'})
    else:
        form = FormContenido(instance=instancia)
        return render(request, 'sitio/editar.html', {'form':form, 'post':instancia})


@login_required
@permission_required('is_superuser')
def editar_articulo(request, ID):
    instancia = Tienda.objects.get(id=ID)
    if request.method == "POST":
        form = FormArticulo(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            post = form.save(commit=False)
            #post.fecha_post = timezone.now()
            post.save()
            #return redirect('ver_post')
            return render(request, 'sitio/mensaje.html', {'msj':'<h2>Articulo editado con exito!!</h2>'})
    else:
        form = FormArticulo(instance=instancia)
        return render(request, 'sitio/editar.html', {'form':form, 'post':instancia})


@login_required
@permission_required('is_superuser')
def editar_usuario(request, ID):
    instancia = User.objects.get(id=ID)
    actual_password = instancia.password
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=instancia)
        if form.is_valid():
            user = form.save(commit=True)
            if check_password(request.POST['password'], actual_password):
                pass
            else:
                user.password = make_password(request.POST['password'])
                
            user.save()
            return render(request, 'sitio/mensaje.html', {'msj':"<h2>Se edito Usuario con exito!!</h2>"})

        else:
            print (form.errors)
            print ('Errors')
    else:
        form = EditUserForm(instance=instancia)

    return render(request, 'sitio/editar_user.html', {'form':form})

@login_required
@permission_required('is_superuser')
def editar_cliente(request, ID):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    instancia = Solicitud.objects.get(id=ID)
    if request.method == "POST":
        form = FormSolicitud(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return render(request, 'sitio/mensaje.html', {'msj':'<h2>Cliente editado con exito!!</h2>'})
    else:
        form = FormSolicitud(instance=instancia)
        return render(request, 'sitio/editar.html', {'form':form, 'post':instancia, "imagenes":servicios})

@login_required
@permission_required('is_superuser')
def borrar_contenido(request, ID):
        instancia = Contenido.objects.get(id=ID)
        instancia.delete()
        return render(request, 'sitio/mensaje.html', {'msj':'<h2>Se elimino el Post con exito!</h2>'})

@login_required
@permission_required('is_superuser')
def eliminar_usuario(request, ID):
    cliente_id = request.GET.get('cli')
    if eval(cliente_id):
        cliente = Cliente.objects.get(id=ID)
        cliente.datos.aprobada = False
        cliente.datos.save()
        cliente.delete()
    else:
        usuario = User.objects.get(id=ID)
        usuario.delete()

    return render(request, 'sitio/mensaje.html', {'msj':'<h2>Se elimino cuenta con exito!</h2>'})

@login_required
def panel_admin(request):
    servicios = Contenido.objects.filter(categoria__icontains="Servicios")
    cliente = []
    if request.user:
        if request.user.is_superuser:
            return render(request, 'sitio/panel.html', {'contenidos':servicios, 'cliente':cliente})
        else:
            return render(request, 'sitio/clientes.html', {'contenidos':servicios})
    else:
        return redirect('/')

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("/") 
