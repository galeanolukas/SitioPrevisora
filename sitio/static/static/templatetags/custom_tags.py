from django import template
from django.utils.safestring import mark_safe
from django.template import Template, Context

register = template.Library() 

@register.tag(name="imagen")
def do_imagen(parser, token):
    nodelist = parser.parse(('endimagen',))
    parser.delete_first_token()
    return ImagenNode(nodelist)

class ImagenNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        
    def render(self, context):
        #code = self.nodelist
        code = self.nodelist.render(context)
        return '<div class="imagen"><a href="%s"><img src="%s"></a></div>' % (code, code)

@register.tag(name="link")
def do_link(parser, token, nombre=None):
    try:
        tag_name, arg = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requiere argumentos" % token.contents.split()[0]
        )
    nodelist = parser.parse(('endlink',))
    parser.delete_first_token()
    return LinkNode(nodelist, nombre=arg)

class LinkNode(template.Node):
    def __init__(self, nodelist, nombre):
        self.nodelist = nodelist
        self.nombre = nombre
        
    def render(self, context):
        #code = self.nodelist
        link = self.nodelist.render(context)
        return '<a class="enlace" href="%s" target="_blank">%s</a>' % (link, self.nombre)

#@register.simple_tag
#def web(link):
#    return mark_safe('<iframe src="%s"></iframe>' % link)

@register.tag(name="web")
def do_web(parser, token):
    nodelist = parser.parse(('endweb',))
    parser.delete_first_token()
    return WebNode(nodelist)

class WebNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        
    def render(self, context):
        #code = self.nodelist
        link = self.nodelist.render(context)
        return '<iframe src="%s"></iframe>' % link


@register.simple_tag
def render_post(post):    
    plantilla = Template("{% load custom_tags %}\n" + post)
    c = Context({'<p>':'<p>'})
    return plantilla.render(c)

@register.tag(name="codigo")
def do_codigo(parser, token):
    nodelist = parser.parse(('endcodigo',))
    parser.delete_first_token()
    return CodigoNode(nodelist)

class CodigoNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        
    def render(self, context):
        #code = self.nodelist
        code = self.nodelist.render(context)
        print (code)
        return '<code style="font-family: monospace; color:yellow; background-color:gray;">%s</code>' % code

@register.tag(name="titulo")
def do_titulo(parser, token, pos=False):
    try:
        tag_name, arg = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requiere argumentos!" % token.contents.split()[0]
        )
    nodelist = parser.parse(('endtitulo',))
    parser.delete_first_token()
    return TituloNode(nodelist, pos=arg)

class TituloNode(template.Node):
    def __init__(self, nodelist, pos):
        self.nodelist = nodelist
        self.pos = pos

    def render(self, context):
        #code = self.nodelist
        code = self.nodelist.render(context)
        if eval(self.pos):
            return '<div id="centrado"><div id="titulo">%s</div></div>' % code
        else:
            return '<div id="titulo">%s</div>' % code
    
@register.tag(name="video")
def do_video(parser, token):
    try:
        tag_name, arg = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requiere argumentos" % token.contents.split()[0]
        )
    nodelist = parser.parse(('endvideo',))
    parser.delete_first_token()
    print (arg)
    return VideoNode(nodelist, auto=arg)

class VideoNode(template.Node):
    def __init__(self, nodelist, auto):
        self.nodelist = nodelist
        if auto == "True":
            self.auto_play = '?autoplay=1'
        else:
            self.auto_play = ''
        
    def render(self, context):
        code = self.nodelist.render(context)
        output = '<div class="video-box"><iframe src="%s%s" frameborder="0" allowfullscreen></iframe></div>' % (code, self.auto_play)
        return output
