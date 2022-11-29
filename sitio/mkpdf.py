# -*- coding: utf-8 -*-
from .tools.fpdf import FPDF
import os


class CuponPdf(FPDF):
    def __init__(self, titulo=None, nombre=None, numero=None, fecha=None, z_name=10):
        FPDF.__init__(self)
        self.dir_current = os.getcwd()
        self.titulo = "CUPON N*: %s" % titulo
        self.msj = "Se sortea el dia Sábado 25 de Junio del 2022"
        self.msj2 = """Participas con el numero de cupón que figura arriba a la derecha, este comprobante es valido hasta el 10/06/2022 en caso de salir premiado."""
        self.nombre = nombre
        self.numero = numero
        self.fecha = fecha
        self.add_page()
        
        self.set_font('Times', 'I', 10)
        self.cell(120)
        self.cell(70, 20, 'NOMBRE Y APELLIDO:', 0, 1)
        if z_name > 20:
            self.set_font('Arial', 'B', 12)
        else:
            self.set_font('Arial', 'B', 15)
            
        self.cell(120)
        self.cell(70, 10, self.nombre, 1, 0, 'C')
        self.ln(10)
        
        self.set_font('Times', 'I', 10)
        self.cell(120) 
        self.cell(70, 20, 'AFILIADO/A N*:', 0, 1)
        self.set_font('Arial', 'B', 15)
        self.cell(120)
        self.cell(70, 10, self.numero, 1, 0, 'C')
        self.ln(10)
        
        self.set_font('Times', 'I', 10)
        self.cell(120)
        self.cell(70, 20, 'FECHA:', 0, 1)
        self.set_font('Arial', 'B', 15)
        self.cell(120)
        self.cell(70, 10, self.fecha, 1, 0, 'C')
        self.ln(10)
        
        self.image(self.dir_current + "/sitio/static/sitio/img/FlayerSorteoT.jpg", 10, 5, 100)
        self.image(self.dir_current + "/sitio/static/sitio/img/banner100.png", 10, 100, 50)
        
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(120)
        # Title
        self.cell(70, 10, self.titulo, 1, 0, 'C')
        # Line break
        self.ln(10)
        
    # Page footer
    def footer(self):
        self.set_font('Arial', 'I', 10)
        self.set_y(-135)
        # Position at 1.5 cm from bottom
        self.cell(0, 10, 'Por consultas o info visite', 0, 0, 'C')
        self.set_y(-130)
        # Arial italic 8
        self.set_font('Arial', 'I', 10)
        # Page number
        self.cell(0, 10, 'www.previsoradelnorte.com', 0, 0, 'C')
        self.set_y(-160)
        # Arial italic 8
        self.set_font('Times', 'B', 12)
        # Page number
        self.cell(0, 10, self.msj, 0, 0, 'C')
        self.set_y(-150)
        self.set_font('Times', 'I', 9)
        # Page number
        self.cell(0, 10, self.msj2, 0, 0, 'C')
