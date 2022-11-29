def plantilla(mensaje):
    template = """
                            <html>
                                <head>
                                <meta name="viewport" content="width=device-width, initial-scale=1">
                                </head>
                                <body style="margin: 0;font-size: 28px;font-family: Arial, Helvetica, sans-serif;">
                                <div class="header" style="background-color: lightgray; color: white;">
                                        <img src="https://www.previsoradelnorte.com/static/sitio/img/logo-pagina.png" alt="">
                                </div>
                                <div class="contenido" style="margin-top: 20px; padding:10px"> 
                                                <div class="fakeimg" style="padding:20px; color: grey; border-radius:15px; font-size: 18px; border: 0.8px solid lightgray;">
                                                	<div id="centrado" style="margin: 0px auto 0px;text-align:center;"><br><div id="titulo" style="color:#728e3a;">%s</div>
               					</div>
               			</div>
                                <footer>
                                               <div id="caja-pie" style="padding: 10px; background:#2d487d; margin-top: 20px; bottom: 0; text-align: center;color: white; font-size: 14px;">
                                                    <p>
                                                    <strong>Visita nuestras redes:</strong><br><br>
                                                    <a href="https://www.facebook.com/laprevisoradelnorte" target="blank">
                                                    	<img src="https://www.previsoradelnorte.com/static/sitio/img/face.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;">
                                                    </a>
                                                    <a href="" >
                                                    <img src="https://www.previsoradelnorte.com/static/sitio/img/tweeter.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;" alt="">
                                                    </a>
                                                    <a href="" >
                                                    <img src="https://www.previsoradelnorte.com/static/sitio/img/instagram.png" style="width:40px; height:40px; border-radius: 50px; border: 1px solid white; padding:5px;" alt="">
                                                    </a>
                                                    </p>
                                                    <p>La Previsora del Norte S.R.L<br><br><span class="copyleft">&copy;</span>Copyleft 2020</p>
                                                    <div class="direccion-bottom" style="text-decoration: none;"><img src="https://www.previsoradelnorte.com/static/sitio/img/ubica-icono.png" style="width: 30px; height: 30px;" /><a style="text-decoration: none; color: white;" href="https://goo.gl/maps/kMesM1AgdZk85Lvz5" target="blank"> Dean Funes 655 - Formosa, Argentina</a></div>
                                                </div>
                                       
                                </footer>
                                </body>
                                </html>

        """ % mensaje

    return template 
