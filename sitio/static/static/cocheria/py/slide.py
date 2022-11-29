from browser import document, html, timer

element = document["slides"]
divs = element.get(selector="div")
info = element.get(selector="aside")
indice = len(divs)
#images = element.attrs

nb = 0
selec = True
    
divs[nb].style.display = "table"
info[nb].style.display ="none"

def cambiar():
    if indice == 1:
        divs[nb].style.display = "table"
        info[nb].style.display = "table"
        pass
    elif selec:
        global nb
        global indice
        divs[nb].style.display = "table"
        info[nb].style.display = "none"
        info[nb - 1].style.display = "none"
        divs[nb - 1].style.display = "none"
        
        if nb == indice - 1:
            nb = 0
        else:
            nb += 1
    else:
        pass
            
def mouseover(ev):
    global selec
    selec = False

def mouseout(ev):
    global selec
    selec = True

for elt_id in ("obituario"):
    document["obituario"].bind('mouseover', mouseover)
    document["obituario"].bind('mouseleave', mouseout)      


timer.set_interval(cambiar, 2500)

