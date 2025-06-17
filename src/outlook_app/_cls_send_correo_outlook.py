# -*- coding: utf-8 -*-
"""
Created By Emerson Aguilar Cruz
"""

import os
import win32com.client
import locale
from pathlib import Path

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

class EnvioCorreoOutlook:

    def __init__(self, destinatarios=None, destinatarios_copia=None, asunto=None, cuerpo_correo=None, texto_adicional=None, 
                 ruta_img=None, archivo=None, ruta_firma=None):
        
        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(self.current_folder))
        self.path_home = str(Path.home())
        self.destinatarios = destinatarios or []
        self.destinatarios_copia = destinatarios_copia or []
        self.asunto = asunto or ""
        self.cuerpo_correo = cuerpo_correo or ""
        self.texto_adicional = texto_adicional or ""
        self.outlook = win32com.client.Dispatch("Outlook.Application")    
        self.ruta_img = os.path.join(self.project_root, 'data', 'img', 'outlook', 'cos_performance')
        self.archivo = archivo
        self.ruta_firma = os.path.join(self.path_home, 'Pictures', 'Firma_Outlook.png')

    def enviar_correo(self):

        try:
            correo = self.outlook.CreateItem(0)
            correo.To = ";".join(self.destinatarios) if isinstance(self.destinatarios, list) else self.destinatarios
            if self.destinatarios_copia:
                correo.CC = ";".join(self.destinatarios_copia) if isinstance(self.destinatarios_copia, list) else self.destinatarios_copia
            correo.Subject = self.asunto
            correo.BodyFormat = 2  # HTML

            # Construcción del cuerpo HTML
            cuerpo_html = f"""<html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                </head>
                <body>
                    <p style="font-family: Arial, sans-serif; font-size: 12pt;">buen_dia</p>
                    <p style="font-family: Arial, sans-serif; font-size: 12pt; white-space: pre-wrap;">{self.cuerpo_correo}</p>"""

            # Agrega imágenes embebidas al HTML
            imagenes = []
            try:
                imagenes = [f for f in os.listdir(self.ruta_img) if f.lower().endswith('.png')]
                for i, nombre_imagen in enumerate(imagenes, 1):
                    cuerpo_html += f"""<br><img src='cid:img_{i}' style='max-width: 800px; width: 100%; height: auto;'><br>"""
            except Exception as e:
                print(f"⚠️ Error al construir HTML para imágenes: {str(e)}")

            # Texto adicional
            if self.texto_adicional:
                cuerpo_html += f"""<br><p style="font-family: Arial, sans-serif; font-size: 12pt;">{self.texto_adicional}</p>"""

            # Firma embebida
            if self.ruta_firma and os.path.exists(self.ruta_firma):
                cuerpo_html += """<br><img src='cid:img_firma' style='max-width: 800px; width: 100%; height: auto;'><br>"""

            cuerpo_html += "</body></html>"

            # Asignación del cuerpo HTML
            correo.HTMLBody = cuerpo_html

            # Adjuntar imágenes después de definir HTMLBody
            for i, nombre_imagen in enumerate(imagenes, 1):
                try:
                    ruta_completa = os.path.join(self.ruta_img, nombre_imagen)
                    adjunto_imagen = correo.Attachments.Add(ruta_completa)
                    adjunto_imagen.PropertyAccessor.SetProperty(
                        "http://schemas.microsoft.com/mapi/proptag/0x3712001F", f"img_{i}"
                    )
                except Exception as e:
                    print(f"⚠️ Error al vincular imagen {nombre_imagen}: {str(e)}")

            # Adjuntar firma
            if self.ruta_firma and os.path.exists(self.ruta_firma):
                try:
                    adjunto_firma = correo.Attachments.Add(self.ruta_firma)
                    adjunto_firma.PropertyAccessor.SetProperty(
                        "http://schemas.microsoft.com/mapi/proptag/0x3712001F", "img_firma"
                    )
                except Exception as e:
                    print(f"⚠️ Error al vincular firma: {str(e)}")

            # Adjuntar archivo
            if self.archivo and os.path.exists(self.archivo):
                correo.Attachments.Add(self.archivo)
            elif self.archivo:
                print(f"⚠️ Advertencia: El archivo adjunto no se encuentra en la ruta {self.archivo}")

            # Enviar el correo
            correo.Send()
            print(f"✅ Correo enviado con éxito a {', '.join(self.destinatarios)}")
            return True

        except Exception as e:
            print(f"❌ Error al enviar el correo: {str(e)}")
            return False
