from browser import bind, document



@bind("#conimagen", 'mouseover')            
def mouseover(ev):
    document["conimagen"].style.opacity = "0.8"
    document["conimagen"].style.transition = "0.4s"    

@bind("#conimagen", 'mouseleave')  
def mouseout(ev):
    document["conimagen"].style.opacity = "0.5"
    document["conimagen"].style.transition = "0.4s" 



