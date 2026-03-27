"""
Created By David Salcedo
Reemplazo de Envio_Pdc_Wpp y EnvioErrorPdc usando el microservicio Node.js
en lugar de Selenium + WhatsApp Web.

El servicio Node debe estar corriendo en http://localhost:3000
Iniciar con: npm run wpp
"""

import os
import requests
from excel_app._cls_excel_auto_manager import Process_Excel


class EnvioWppHttp:
    """
    Envia imagenes y textos a grupos de WhatsApp llamando al microservicio Node.js.
    Reemplaza a Envio_Pdc_Wpp eliminando la necesidad de Selenium para WhatsApp.
    """

    WPP_URL = "http://localhost:3000"

    def __init__(self, processor: Process_Excel):
        self.ruta_img      = processor.ruta_img
        self.ruta_txt      = processor.ruta_txt
        self.var_captura_img = processor.var_captura_img

    def _verificar_servicio(self):
        """Verifica que el microservicio Node este activo y conectado a WhatsApp."""
        try:
            r = requests.get(f"{self.WPP_URL}/status", timeout=5)
            estado = r.json()
            if not estado.get("listo"):
                raise RuntimeError("El cliente WhatsApp no esta listo. Verifica npm run wpp.")
        except requests.ConnectionError:
            raise RuntimeError(
                f"No se puede conectar al servicio WhatsApp en {self.WPP_URL}. "
                "Ejecuta: npm run wpp"
            )

    def env_pdc_bot(self):
        self._verificar_servicio()

        for grupo in self.var_captura_img:
            nombre_hoja  = grupo['hojas_captura_img']
            nombre_grupo = grupo['nombre_grupo']

            imagen_path = os.path.join(self.ruta_img, f"{nombre_hoja}.jpg")
            texto_path  = os.path.join(self.ruta_txt, f"{nombre_hoja}.txt")

            # Leer caption desde el .txt generado por copiar_celdas_txt
            caption = ""
            if os.path.exists(texto_path):
                with open(texto_path, 'r', encoding='utf-8') as f:
                    caption = f.read().strip()

            if not os.path.exists(imagen_path):
                print(f"Imagen no encontrada: {imagen_path}")
                continue

            try:
                r = requests.post(
                    f"{self.WPP_URL}/send-image",
                    json={
                        "group":      nombre_grupo,
                        "image_path": imagen_path,
                        "caption":    caption
                    },
                    timeout=60
                )
                data = r.json()
                if data.get("ok"):
                    print(f"Imagen enviada a '{nombre_grupo}'")
                else:
                    print(f"Error enviando a '{nombre_grupo}': {data.get('error')}")
            except Exception as e:
                print(f"Error en envio a '{nombre_grupo}': {e}")


class EnvioErrorHttp:
    """
    Envia mensaje de alerta de error a WhatsApp llamando al microservicio Node.js.
    Reemplaza a EnvioErrorPdc.
    """

    WPP_URL     = "http://localhost:3000"
    GRUPO_ALERTA = "Mediciones Data strategies Latam"

    def __init__(self, tabla_alerta=None, diferencia_minutos=None):
        self.tabla_alerta       = tabla_alerta
        self.diferencia_minutos = diferencia_minutos
        self.mensaje_alerta = (
            f"Se confirma error: La tabla de marcaciones {self.tabla_alerta} "
            f"ubicada en el servidor 172.70.7.61 "
            f"no se ha actualizado en mas de {self.diferencia_minutos:.0f} minutos. "
            f"*Lideres De Data Strategies* Su ayuda escalándolo."
        )

    def bot_envio_error(self):
        try:
            r = requests.post(
                f"{self.WPP_URL}/send-text",
                json={
                    "group":   self.GRUPO_ALERTA,
                    "message": self.mensaje_alerta
                },
                timeout=30
            )
            data = r.json()
            if data.get("ok"):
                print(f"Alerta enviada al grupo '{self.GRUPO_ALERTA}'")
            else:
                print(f"Error enviando alerta: {data.get('error')}")
        except Exception as e:
            print(f"Error en envio de alerta: {e}")
