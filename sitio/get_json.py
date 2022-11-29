# -*- coding: utf-8 -*-
from urllib.request import urlopen
import json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


class Get(object):
    def __init__(self):
        self.respuesta = None

    def consulta(self, url):
        with urlopen(url, context=ctx) as response:
            body = response.read()
            if body == b'No se encontro la persona':
                return False
            else:
                self.respuesta = json.loads(body)
                return True


    
