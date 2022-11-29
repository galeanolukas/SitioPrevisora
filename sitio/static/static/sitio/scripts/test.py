from browser import document
from browser.widgets.dialog import InfoDialog

def click(ev):
    InfoDialog("Hello", f"Hello, {document['entrada'].value} !")

document["Button"].bind("click", click) 
