# -*- coding: utf-8 -*-
def plantilla(mensaje=[]):
    template = """
                            <html>
                                <head>
                                        <meta name="viewport" content="width=device-width, initial-scale=1">
                                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                                        <title>COCHERIA SAN FRANCISCO | HOMENAJES</title>
                                        <style type="text/css">body {margin: 0; padding: 0; min-width: 100&#37;; font-size: 28px;font-family: Arial, Helvetica, sans-serif;} .content {width: 100&#37;; max-width: 600px;}</style>
                                </head>
                                <body>
                                <div class="header" style="background-color: #804000; color: white;">
                                        <img src="https://www.previsoradelnorte.com/static/cocheria/img/Banner.png" alt="Logo">
                                </div>
                                <div class="content" style="margin-top: 20px; padding:10px"> 
                                                <div class="fakeimg" style="padding:20px; color: grey; border-radius:15px; font-size: 18px; border: 0.8px solid lightgray;">
                                                	<div id="centrado" style="margin: 0px auto 0px;text-align:center;"><br><div id="titulo" style="color:gray;">
                                                	<div class="avatar" style="height: 200px; width: 200px; border-radius: 50&#37;; margin-left: auto; margin-right:auto; padding:auto; z-index:100; border: 2px solid white; ">
                                                        <img src="www.previsoradelnorte.com/sanfrancisco/%s" alt="ImagenObituario"/>
                                                    </div><br><br><hr>%s<hr><p>De parte de <strong>%s</strong></p></div>
               					</div>
               			</div>
                                <footer>
                                               <div id="caja-pie" style="padding: 10px; background:#804000; margin-top: 20px; bottom: 0; text-align: center;color: white; font-size: 14px;">
                                                    <p>
                                                    <strong>Visita nuestras redes:</strong><br><br>
                                                    <a href="https://www.facebook.com/laprevisoradelnorte" target="blank">
                                                    	<img src="https://www.previsoradelnorte.com/static/cocheria/img/face.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;">
                                                    </a>
                                                    <a href="" >
                                                    <img src="https://www.previsoradelnorte.com/static/cocheria/img/tweeter.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;" alt="">
                                                    </a>
                                                    <a href="" >
                                                    <img src="https://www.previsoradelnorte.com/static/cocheria/img/instagram.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;" alt="">
                                                    </a>
                                                    </p>
                                                    <p>COCHERIA SAN FRANCISCO<br><br><span class="copyleft">&copy;</span>Copyleft 2020</p>
                                                    <div class="direccion-bottom" style="text-decoration: none;"><img src="https://www.previsoradelnorte.com/static/cocheria/img/ubica-icono.png" style="width: 30px; height: 30px;" /><a style="text-decoration: none; color: white;" href="https://goo.gl/maps/CqwAc4Kq54Eo26f68" target="blank">Espana 441 - Formosa, Argentina</a></div>
                                                </div>
                                       
                                </footer>
                                </body>
                                </html>

        """ % (mensaje[0], mensaje[1], mensaje[2])

    return template 
