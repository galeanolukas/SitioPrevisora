from browser import bind, document 


@bind("#bot-whattsapp", "click")
def change(event):
    display = document["info-num"].style.display
    if display == "none":
        document["info-num"].style.transition = "0.5s"
        document["info-num"].style.display = "inline"
        document["info-num"].style.background = "green"
    else:
        document["info-num"].style.display = "none"
