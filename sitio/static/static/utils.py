from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
#
from mercadopago import SDK
from xhtml2pdf import pisa
import os 

def render2pdf(template_src, context_dict, file_name):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = open(os.getcwd() + file_name, 'wb')
    response = result.name
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        result.close()
        return HttpResponse(response, content_type='application/pdf')

    
    else:
        return None


class MPCheckOut(SDK):
    def __init__(self, cuenta=None):
        SDK.__init__(self, cuenta.access_token)
        self.cuenta = cuenta
        self.preferencias = {}
        self.boton_js = '''
                                // Agrega credenciales de SDK
                              const mp = new MercadoPago('{{ %s }}', {
                                                        locale: 'es-AR'
                                });

                                // Inicializa el checkout
                              mp.checkout({
                                  preference: {
                                id: '{{ %s }}'
                                },
                                render: {
                                    container: '.mp_boton', // Indica el nombre de la clase donde se mostrará el botón de pago
                                    label: '%s', // Cambia el texto del botón de pago (opcional)
                                  }
       
                                });'''


    def config(self, titulo='Pago', monto=0, unidad=1, ID='service'):
        self.preferencias['items'] = [{'id':ID, 'title':titulo, 'quantity':unidad, 'unit_price':monto}]

    def respuestas_urls(self, exito, fallo, pendiente):
        self.preferencias["auto_return"] = "approved"
        self.preferencias['back_urls'] = {'success':exito, 'pending':pendiente, 'failure':fallo}
        
    def boton(self, label='REALIZAR PAGO'):
        self.api = self.preference().create(self.preferencias)['response']
        print (self.api)
        return self.boton_js % (self.cuenta.public_key, self.api['id'], label)
    
    
    
    
