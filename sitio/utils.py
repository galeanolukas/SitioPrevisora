from io import BytesIO, StringIO
from django.http import HttpResponse
from django.template.loader import get_template
#
from mercadopago import SDK
from xhtml2pdf import pisa
import os
import string 
import random 

def Key(digit=4):
    keylist = [random.choice(base_str()) for i in range(digit)] 
    return ("".join(keylist)) 
    
def base_str(): 
    return (string.ascii_letters+string.digits) 

def render2pdf(template_src, context_dict, file_name=None):
    template = get_template(template_src)
    html = template.render(context_dict)
    if file_name:
        result = open(os.getcwd() + file_name, 'wb')
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        result.close()
        result = open(os.getcwd() + file_name, 'rb')
        response = HttpResponse(result.read(), content_type='application/pdf')
        result.close() 
    else:
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
            
    if not pdf.err:
        return response
           
    return None

class MPCheckOut(SDK):
    def __init__(self, cuenta=None):
        SDK.__init__(self, cuenta.access_token)
        self.cuenta = cuenta
        self.preferencias = {}
        self.boton_js = '''

                        // Agrega credenciales de SDK
			const mp = new MercadoPago("%s", {
			    locale: "es-AR",
			});
			const checkout = mp.checkout({
			   preference: {
			       id: "%s",
			   },
			   render: {
			       container: ".cho-container",
			       label: "%s",
			    }
			});'''


    def config(self, titulo='Pago', monto=0, unidad=1, ID='service'):
    	if 'items' in self.preferencias.keys():
    	    self.preferencias['items'].append({'id':ID, 'title':titulo, 'quantity':unidad, 'unit_price':monto})
    	else:
    	    self.preferencias['items'] = [{'id':ID, 'title':titulo, 'quantity':unidad, 'unit_price':monto}]

    def respuestas_urls(self, exito, fallo, pendiente):
        self.preferencias["auto_return"] = "approved"
        self.preferencias['back_urls'] = {'success':exito, 'pending':pendiente, 'failure':fallo}
        
    def boton(self, label='REALIZAR PAGO'):
        self.api = self.preference().create(self.preferencias)['response']
        print (self.api)
        return self.boton_js % (self.cuenta.public_key, self.api['id'], label)
    
    
    
    
