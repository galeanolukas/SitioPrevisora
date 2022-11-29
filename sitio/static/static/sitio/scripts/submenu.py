from browser import document, html

barra = document["Barra"]
items = barra.get(selector="a")

subbarra = document["Subbarra"]
subitems = subbarra.get(selector="a")

menu = None
opciones = [] 


def showmenu(opciones):
    for sub in subitems:
        a = sub.attrs.get('id')
        if a is None:
            pass
        else:
            sub.style.display = "block"

def mousesobre(ev):
    global menu
    for p in items:
        if p.attrs.get('id') is None:
            pass

        else:
            print (p.attrs.get('id'))
   
def mousefuera(ev):
    print ("dejo")
    pass


#busca item del menu principal con submenu
for item in items:
    global menu_selec
    menu_selec = item.attrs.get('id')
    if menu_selec is None:
        pass
    else:
        opciones.append(menu_selec)
        #document[item.attrs.get('id')].bind('mouseover', mousesobre)
        #document[item.attrs.get('id')].bind('mouseleave', mousefuera)
        document[menu_selec].bind('click', lambda ev:showmenu(opciones))


            

