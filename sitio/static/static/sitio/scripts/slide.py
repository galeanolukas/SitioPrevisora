from browser import document, html, timer

element = document["slides"]
images = element.get(selector="div")
info = element.get(selector="header")
indice = len(images)
#images = element.attrs

nb = 0
selec = True

#print (len(element))
#for img in images:
#    print (img.attrs.get("src"))
    
images[nb].style.display = "block"
#info[nb].display ="block"

def change():
    if selec:
        global nb
        global indice
        images[nb].style.display = "block"
        #info[nb].style.display = "block"

        images[nb - 1].style.display = "none"
        images[nb - 1].style.transition = "opacity 200ms linear"
        #info[nb - 1].style.display = "none"
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


for elt_id in ("slides"):
    document["slides"].bind('mouseover', mouseover)
    document["slides"].bind('mouseleave', mouseout)      


timer.set_interval(change, 3000)

