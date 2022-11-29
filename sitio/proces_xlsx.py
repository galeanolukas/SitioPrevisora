import xlrd
from random import randint


class CargarPlanilla(object):
    def __init__(self, path_xlsx=None):

        self.planilla = xlrd.open_workbook(path_xlsx)

        self.pagina = self.planilla.sheet_by_index(0)

        self.filas = self.pagina.nrows
        self.columnas = self.pagina.ncols

        self.resultados = ()

        #self.pagina.cell_value(0, 0)

    def buscar_fila(self, busqueda=None, n_colum=None):
        for fila in range(8, self.filas-1):
            for elem in self.pagina.row_values(fila):
                if elem == busqueda:
                    #self.resultados = self.resultados + tuple([self.pagina.row_values(fila)])
                    print (elem)
                    self.resultados = self.resultados + tuple([self.pagina.row_values(fila)])
                
        return self.resultados

    def buscar_aleatorio(self, b=None, n=None):
        
        #num_random = cupones[randint(0, cupones.count() - 1)]
        pass

    
    
    
