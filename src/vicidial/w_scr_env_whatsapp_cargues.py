# -- coding: utf-8 --
"""
Created on Tue Apr  9 13:49:57 2024
@Author: Emerson.Aguilar

"""

import time
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

usuario_red = 'Emerson.Aguilar'
xpath_buscar_chats = '//*[@id="side"]/div[1]/div/div[2]/div/div/div[1]/p'
xpath_boton_adjun = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/button'
xpath_input_img = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'

class SendPDC:
    def __init__(self, varProfilePath, varDriverPath, arrGroups, imgFolder):
        self.varProfilePath = varProfilePath
        self.varDriverPath = varDriverPath
        self.arrGroups = arrGroups
        self.imgFolder = imgFolder
    
    def webdriver_pp_dp(self):
        options = Options()
        options.add_argument(f'user-data-dir={self.varProfilePath}')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        service = Service(executable_path=self.varDriverPath)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver

    def bot_send_all_pdc(self):
        try:
            driver = self.webdriver_pp_dp()
            driver.get('https://web.whatsapp.com/')
            WebDriverWait(driver, 150).until(EC.visibility_of_element_located((By.ID, 'side')))

            # Obtener todas las imágenes de la carpeta
            imagenes = [img for img in os.listdir(self.imgFolder) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            for grupo in tqdm(self.arrGroups, desc='Send PDC'):
                for img in imagenes:
                    try:
                        ruta_imagen = os.path.join(self.imgFolder, img)
                        texto_a_enviar = f"lista cargada - {os.path.splitext(img)[0]}"

                        # Buscar el grupo en WhatsApp
                        buscar_chats = WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_buscar_chats))
                        )
                        buscar_chats.click()
                        time.sleep(3)
                        buscar_chats.clear()
                        time.sleep(3)
                        buscar_chats.send_keys(grupo['nombre'])

                        time.sleep(3)
                        buscador_grupo = f'//span[@title="{grupo["nombre"]}"]'
                        grupo_elemento = WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.XPATH, buscador_grupo))
                        )
                        grupo_elemento.click()

                        time.sleep(3)
                        adjuntar_button = WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_boton_adjun))
                        )
                        adjuntar_button.click()

                        time.sleep(3)
                        input_archivo = WebDriverWait(driver, 60).until(
                            EC.presence_of_element_located((By.XPATH, xpath_input_img))
                        )
                        input_archivo.send_keys(ruta_imagen)

                        time.sleep(3)
                        campo_texto_xpath = '//div[@aria-placeholder="Add a caption"]'
                        elemento_destino = WebDriverWait(driver, 60).until(
                            EC.presence_of_element_located((By.XPATH, campo_texto_xpath))
                        )
                        elemento_destino.click()
                        elemento_destino.send_keys(texto_a_enviar)

                        time.sleep(3)
                        boton_enviar_xpath = '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]'
                        boton_enviar = WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.XPATH, boton_enviar_xpath))
                        )
                        boton_enviar.click()

                        time.sleep(7)  # Puedes ajustar este tiempo si lo ves muy largo o muy corto
                    except Exception as e:
                        print(f"Error al enviar imagen {img} al grupo {grupo['nombre']}: {e}")
        except Exception as e:
            print(f"Error general en el bot: {e}")
        finally:
            driver.quit()

    def main(self):
        self.bot_send_all_pdc()


if __name__ == "__main__":
    varProfilePath = rf'C:\Users\{usuario_red}\AppData\Local\Google\Chrome\User Data\Default\SeleniumProfile'
    varDriverPath = rf'C:\Users\{usuario_red}\Documents\chromedriver.exe'
    imgFolder = rf'C:\Users\{usuario_red}\Documents\git_hub\Chubb\data\img\load_vcdl'
    
    arrGroups = [
        {'nombre': 'INFORMES Y REPORTES CHUBB'}
    ]
    
    pdc = SendPDC(varProfilePath, varDriverPath, arrGroups, imgFolder)
    pdc.main()
