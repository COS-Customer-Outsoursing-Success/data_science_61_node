"""
Created By Emerson Aguilar Cruz
"""

import time
import os
import glob
import json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from web_scraping._cls_webscraping import WebScraping_Chrome

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_folder))

class LoadListVcdl:
    def __init__(self, ruta_cargue_vicidial=None, user_vcdl=None, pass_vcdl=None, server_vcdl=None, activo=None, opcion_copiado=None, 
                 indicativo_pais=None):

        # -- Config driver path -- 
        self.path_home = str(Path.home())  # -----> Esto devuelve "C:\Users\tu_usuario"
        self.driver_path = os.path.join(
        self.path_home, 
        'Documents',
        'chromedriver.exe'
        )
      
        # -- Config Vicidial -- 
        self.user_vcdl = user_vcdl 
        self.pass_vcdl = pass_vcdl
        self.server_vcdl = server_vcdl
        self.activo = activo
        self.opcion_copiado = opcion_copiado
        self.indicativo_pais = indicativo_pais 

        # -- Config Rutas -- 
        self.ruta_cargue_vicidial = ruta_cargue_vicidial
        self.ruta_subida = os.path.dirname(self.ruta_cargue_vicidial)
        self.archivos = os.listdir(self.ruta_cargue_vicidial)
        self.archivos_xlsx = [archivo for archivo in self.archivos if archivo.endswith(".csv")]
        self.ruta_img = os.path.join(project_root, 'data', 'img','load_vcdl')

        # -- Config campanas -- 
        self.json_campanas = os.path.join(project_root, 'config', 'config_campanas.json')
        with open(self.json_campanas, "r") as file_json_campanas:
            self.config_campanas = json.load(file_json_campanas)

        # -- Config xpath --
        self.json_xpaths = os.path.join(project_root, 'config', 'xpaths_config.json')
        with open(self.json_xpaths, "r") as file_json_xpath:
            self.config_xpaths = json.load(file_json_xpath)

        # -- Config campos personalizados --
        self.json_custom_fields = os.path.join(project_root, 'config', 'custom_fields.json')
        with open(self.json_custom_fields, "r") as file_json_custom_fields:
            self.config_custom_fields = json.load(file_json_custom_fields)
        
        self.hoy = datetime.now().strftime('%Y-%m-%d') 

    def delete_img_load(self):
        if os.path.exists(self.ruta_img):
            archivos = glob.glob(os.path.join(self.ruta_img, '*'))
            for archivo in archivos:
                os.remove(archivo)
                print(f'Archivo eliminado: {archivo}')
        else:
            print(f'Ruta no encontrada: {self.ruta_img}')

    def cargar_vicidial(self):
        print("Eliminando imágenes de listas cargadas")
        self.delete_img_load()
        
        if not self.archivos_xlsx:
            print("⚠️ No se encontró ningún archivo .csv en la carpeta")
            return

        for nombre_archivo_cargue in self.archivos_xlsx:
            print(f"\n📦 Procesando archivo: {nombre_archivo_cargue}")
            ruta_archivo_cargue = os.path.join(self.ruta_cargue_vicidial, nombre_archivo_cargue)
            
            driver = WebScraping_Chrome.Webdriver_ChrDP(self.driver_path)

            try:

                nombre_base = nombre_archivo_cargue.split('-')[0].strip()
                if nombre_base not in self.config_campanas:
                    nombre_base = nombre_archivo_cargue.split(' -')[0].strip()

                if nombre_base not in self.config_campanas:
                    raise KeyError(f"Campaña '{nombre_base}' no configurada en config_campanas.json")

                campana_config = self.config_campanas[nombre_base]

                campos_requeridos = ['campana_vicidial', 'campaign_id', 'numero_maximo_listas']
                for campo in campos_requeridos:
                    if campo not in campana_config:
                        raise ValueError(f"Campo requerido '{campo}' faltante en configuración para {nombre_base}")

                campana_vicidial = str(campana_config["campana_vicidial"])
                campaign_id = str(campana_config["campaign_id"])
                numero_maximo_listas = int(campana_config["numero_maximo_listas"])

            except KeyError as e:
                print(f"Error al acceder a la configuración de campaña: {e}")
                continue

            except ValueError as e:
                print(f"Error de valor: {e}")
                continue 

            except Exception as e:
                print(f"Error inesperado: {e}")
                continue 

            url = (
                f"http://{self.user_vcdl}:{self.pass_vcdl}@"
                f"{self.server_vcdl}/vicidial/admin.php?"
                f"ADD=34&campaign_id={campana_vicidial}"
            )
            
            print(f"🎯 Configuración obtenida - Campaña: {campana_vicidial}")
            print(f"🔗 URL generada: {url.split('@')[0]}*****@{url.split('@')[1]}")
        
            try:
                WebScraping_Chrome.WebScraping_Acces(driver, url)
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_campaign_cargada"])
                print("✅ Página cargada correctamente")
            
            except Exception as e:
                print(f"Error al abrir url de vicidial debido a {e}")
                continue

            try:
                print("⏳ Esperando lista de cargue existente...")

                element = WebDriverWait(driver, 150).until(EC.presence_of_element_located((By.ID, "last_list_statuses")))

                values = element.get_attribute("value").split('|')
                
                list_numbers = [int(val) for i, val in enumerate(values) if i % 2 == 0 and val.isdigit()]
                
                if not list_numbers:
                    raise ValueError("No se encontraron números en la lista de cargue.")
                
                max_list = max(list_numbers)                
                print(f"🔢 Lista de cargue más alta detectada: {max_list}")
                lista_crear = max_list + 1
                print(f"🔢 Lista de cargue a crear: {lista_crear}")

                checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[name="list_active_change[]"]')
                for checkbox in checkboxes:
                    if checkbox.is_selected():
                        list_id = checkbox.get_attribute('value')
                        print(f"🔘 Checkbox con valor {list_id} está ACTIVO - Desactivando...")
                        
                        # Primero desmarcar (si es necesario)
                        checkbox.click()  # Esto cambia el estado checked
                        
                        # Verificar que realmente se desmarcó
                        if checkbox.is_selected():
                            print(f"⚠️ El checkbox {list_id} no se desmarcó correctamente, usando JavaScript")
                            driver.execute_script("arguments[0].checked = false;", checkbox)
                        
                        # Luego deshabilitar
                        driver.execute_script("""
                            arguments[0].disabled = true;
                            arguments[0].style.opacity = '0.5';
                            arguments[0].style.cursor = 'not-allowed';
                        """, checkbox)

                        WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_submit_enviar_cambios_lista"])
                        WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_submit_enviar_cambios_lista"])
                        time.sleep(1)
                                
                        print(f"✅ Checkbox {list_id} desactivado y deshabilitado")
                    else:
                        print(f"⚪ Checkbox con valor {checkbox.get_attribute('value')} ya está INACTIVO")

            except Exception as e:
                print(f"🚨 Ocurrió un error: {str(e)}")


                if max_list >= numero_maximo_listas:
                    for _ in range(7):
                        print("⚠️ Advertencia: El número de lista excede el máximo asignado. Validar con telecomunicaciones.")
                    driver.quit()
            except Exception as e:        
                print(f"⚠️ Error al crear lista ya que excede el numero de listas permitidas")
                continue

            try:    
                print("📝 Creando nueva lista...")
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_boton_listas"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_boton_listas"])
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_crear_lista"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_crear_lista"])
                time.sleep(1)

                campos = [
                    (self.config_xpaths["xpath_lista_id"], lista_crear),
                    (self.config_xpaths["xpath_name"], f"{lista_crear} - {campana_vicidial}"),
                    (self.config_xpaths["xpath_list_description"], f"{lista_crear} - {campana_vicidial}"),
                    (self.config_xpaths["xpath_campaign"], campaign_id),
                    (self.config_xpaths["xpath_active"], self.activo)
                ]

                for xpath, valor in campos:
                    print(f"✍️ Llenando campo {xpath} con valor: {valor}")
                    WebScraping_Chrome.WebScraping_Wait(driver, 150, xpath)
                    WebScraping_Chrome.WebScraping_Keys(driver, xpath, valor)
                    time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_submit_crear"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_submit_crear"])
                print("📋 Lista creada exitosamente. Copiando Campos Personalizados")
                time.sleep(1)
                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_copiar_campos"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_copiar_campos"])
                time.sleep(1)
                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_copiar_desde_lista"])
                WebScraping_Chrome.WebScraping_Keys(driver, self.config_xpaths["xpath_copiar_desde_lista"], max_list)
                time.sleep(1)
                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_copiar_a_lista"])
                WebScraping_Chrome.WebScraping_Keys(driver, self.config_xpaths["xpath_copiar_a_lista"], f"{lista_crear} - {lista_crear} - {campana_vicidial}")
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_opcion_de_copiado"])
                WebScraping_Chrome.WebScraping_Keys(driver, self.config_xpaths["xpath_opcion_de_copiado"], self.opcion_copiado)
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_submit_copiar"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_submit_copiar"])
                time.sleep(1)

                print("📁 Iniciando carga de archivo...")
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_cargar_contactos"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_cargar_contactos"])
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_adjuntar_archivo"])
                WebScraping_Chrome.WebScraping_Keys(driver, self.config_xpaths["xpath_adjuntar_archivo"], ruta_archivo_cargue)
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_list_id_cargar"])
                WebScraping_Chrome.WebScraping_Keys(driver, self.config_xpaths["xpath_list_id_cargar"], f"{lista_crear} - {lista_crear} - {campana_vicidial}")
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_indicativo_pais"])
                WebScraping_Chrome.WebScraping_Select(driver, "phone_code_override", self.indicativo_pais)
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_plantilla_personalizado"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_plantilla_personalizado"])
                time.sleep(1)

                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_submit_enviar_contactos"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_submit_enviar_contactos"])
                time.sleep(1)
                print("🧬 Esperando tabla de campos personalizados...")

                tabla = WebScraping_Chrome.WebScraping_Wait(driver, 600, self.config_xpaths["xpath_tabla_campos_personalizados"])
                print("✅ Tabla encontrada.")
                
                time.sleep(3)

                campos_campana = self.config_custom_fields.get(nombre_base, {})

                filas = driver.find_elements(By.XPATH, "//tr[@bgcolor='#69D3E0']")
                print(f"📊 Total de filas de campos personalizados encontradas: {len(filas)}")

                for i, fila in enumerate(filas):
                    columnas = fila.find_elements(By.TAG_NAME, "td")
                    if len(columnas) < 2:
                        continue

                    clave = columnas[0].text.strip()

                    try:
                        select_element = columnas[1].find_element(By.TAG_NAME, "select")
                        if clave in campos_campana:
                            valor_a_seleccionar = campos_campana[clave]
                            select_element.send_keys(valor_a_seleccionar)
                            print(f'✅ {clave} asignado a {valor_a_seleccionar} (Campaña: {nombre_base})')
                        else:
                            print(f'⚠️ {clave} no está en el mapping para {nombre_base}, se deja vacío.')
                    except NoSuchElementException:
                        print(f'⚠️ Campo {clave} no tiene elemento select, se omite')
                    except Exception as e:
                        print(f'❌ Error en asignación del campo {clave}: {str(e)}')

                print("📤 Enviando para el cargue final...")
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_submit_cargar_final"])
                WebScraping_Chrome.WebScraping_Nav(driver, self.config_xpaths["xpath_submit_cargar_final"])
                time.sleep(1)

                print("⏳ Esperando finalización de carga...")
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.config_xpaths["xpath_cargado_final"])
                print("✅ Lista Cargada Sin Problema")

                self.ruta_imagen = os.path.join(project_root, 'data', 'img', 'load_vcdl', f'{nombre_archivo_cargue}.png')

                imagen = driver.get_screenshot_as_file(self.ruta_imagen)
                print(f"📸 Captura guardada en: {self.ruta_imagen}")

            except Exception as e:
                print(f"❌ Error general durante el proceso: {e}")
            
            time.sleep(5)

            try:
                print("📁 Moviendo archivo procesado a la carpeta de 'Cargados'...")
                target_folder = os.path.join(self.ruta_subida, "Cargado", campana_vicidial, self.hoy)
                
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                    print(f"📂 Carpeta {target_folder} creada.")

                nueva_ruta = os.path.join(target_folder, nombre_archivo_cargue)
                if not os.path.exists(nueva_ruta):
                    os.rename(ruta_archivo_cargue, nueva_ruta)
                    print(f"✅ Archivo {nombre_archivo_cargue} movido a {nueva_ruta}")
                else:
                    print(f"⚠️ El archivo {nombre_archivo_cargue} ya existe en la carpeta de cargados.")

            except Exception as e:
                print(f"❌ Error al mover el archivo: {e}")
            finally:
                print("🚪 Cerrando navegador.")
                driver.quit()