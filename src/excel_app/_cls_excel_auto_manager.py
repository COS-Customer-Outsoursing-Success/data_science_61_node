"""""
Created By Emerson Aguilar Cruz
"""""
import win32com.client
import win32clipboard
import warnings
import time
import psutil
import pythoncom
import glob
import os
import pandas as pd
import tqdm
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab
from web_scraping._cls_webscraping import WebScraping_Chrome
import threading
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from conexiones_db._cls_sqlalchemy import MySQLConnector

class EjecucionStoredProcedure:

    def __init__(self, schema, stored_procedures=None):
        self.schema = schema
        self.stored_procedures = stored_procedures or []
        self.parar_sp = threading.Event()

    def _cargar_indicador(self):
        while not self.parar_sp.is_set():
            for symbol in "|/-\\":
                print(f"\rEjecutando SP... {symbol}", end="", flush=True)
                time.sleep(0.1)
                if self.parar_sp.is_set():
                    break

    def ejecutar_sps(self):
        try:
            print("Conectando a MySQL usando SQLAlchemy...")
            engine = MySQLConnector.get_connection(database=self.schema)

            with engine.connect() as conexion:
                print("Conexión exitosa.")

                for sp in self.stored_procedures:
                    nombre = sp['nombre']
                    parametros = sp.get('parametros', {})

                    print(f"\nEjecutando Stored Procedure: {nombre}")
                    self.parar_sp.clear()
                    hilo_carga = threading.Thread(target=self._cargar_indicador)
                    hilo_carga.start()

                    try:
                        if parametros:
                            placeholders = ', '.join(f":{k}" for k in parametros)
                            sql = text(f"CALL {nombre}({placeholders})")
                            conexion.execute(sql, parametros)
                        else:
                            conexion.execute(text(f"CALL {nombre}()"))

                        print(f"\nSP '{nombre}' ejecutado correctamente.")
                    except Exception as e:
                        print(f"Error al ejecutar '{nombre}': {e}")
                    finally:
                        self.parar_sp.set()
                        hilo_carga.join()
                        time.sleep(1)

                print("Todos los Stored Procedures se ejecutaron.")

        except SQLAlchemyError as e:
            print(f"Error general al ejecutar SPs: {e}")
        finally:
            if 'engine' in locals():
                engine.dispose()
                print("Conexión cerrada.")

class Process_Excel:
    def __init__(self, archivo_excel=None, var_captura_img=None, ruta_img=None, 
                 ruta_txt=None, profile_path=None, driver_path=None, diferencia_minutos=None, tabla_alerta=None,
                 schema=None, stored_procedures=None):
        self.path_home = str(Path.home())  # -----> Esto devuelve "C:\Users\tu_usuario"
        self.profile_path = profile_path
        self.driver_path = os.path.join(
            self.path_home, 
            'Documents',
            'chromedriver.exe'
        )
        self.url = 'https://web.whatsapp.com/'
        self.archivo_excel = archivo_excel
        self.var_captura_img = var_captura_img
        self.ruta_img = ruta_img
        self.ruta_txt = ruta_txt
        os.makedirs(self.ruta_img, exist_ok=True)
        os.makedirs(self.ruta_txt, exist_ok=True)
        self.xpath_buscar_chats = '//div[@aria-placeholder="Search or start a new chat"]' 
        self.xpath_boton_adjun = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/button'
        self.xpath_input_img = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
        self.xpath_mensaje = '//div[@aria-placeholder="Add a caption"]'
        self.xpath_boton_enviar = '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]'
        self.xpath_wpp = '//*[@id="app"]/div/div[3]/div/div[3]/header/header'
        self.schema = schema
        self.stored_procedures = stored_procedures or []
        self.parar_sp = threading.Event()

    def _cargar_indicador(self):
        while not self.parar_sp.is_set():
            for symbol in "|/-\\":
                print(f"\rEjecutando SP... {symbol}", end="", flush=True)
                time.sleep(0.1)
                if self.parar_sp.is_set():
                    break

    def ejecutar_sps(self):
        try:
            print("Conectando a MySQL usando SQLAlchemy...")
            engine = MySQLConnector.get_connection(database=self.schema)

            with engine.connect() as conexion:
                print("Conexión exitosa.")

                for sp in self.stored_procedures:
                    nombre = sp['nombre']
                    parametros = sp.get('parametros', {})

                    print(f"\nEjecutando Stored Procedure: {nombre}")
                    self.parar_sp.clear()
                    hilo_carga = threading.Thread(target=self._cargar_indicador)
                    hilo_carga.start()

                    try:
                        if parametros:
                            placeholders = ', '.join(f":{k}" for k in parametros)
                            sql = text(f"CALL {nombre}({placeholders})")
                            conexion.execute(sql, parametros)
                        else:
                            conexion.execute(text(f"CALL {nombre}()"))

                        print(f"\nSP '{nombre}' ejecutado correctamente.")
                    except Exception as e:
                        print(f"Error al ejecutar '{nombre}': {e}")
                    finally:
                        self.parar_sp.set()
                        hilo_carga.join()
                        time.sleep(1)

                print("Todos los Stored Procedures se ejecutaron.")

        except SQLAlchemyError as e:
            print(f"Error general al ejecutar SPs: {e}")
        finally:
            if 'engine' in locals():
                engine.dispose()
                print("Conexión cerrada.")

    def delete_archivos_ruta(self):
        """Elimina todos los archivos dentro de las rutas especificadas."""

        for dir_existentes in (self.ruta_txt, self.ruta_img):
            if not os.path.exists(dir_existentes):
                print(f"Ruta '{dir_existentes}' no existe, creando folder.")
                os.makedirs(dir_existentes)

        for ruta in [self.ruta_img, self.ruta_txt]:
            if os.path.exists(ruta):
                archivos = glob.glob(os.path.join(ruta, '*'))
                for archivo in archivos:
                    try:
                        os.remove(archivo)
                        print(f'Archivo eliminado: {archivo}')
                    except Exception as e:
                        print(f'Error al eliminar {archivo}: {e}')
            else:
                print(f'Ruta no encontrada: {ruta}')

    def kill_excel(self):
        """Cierra todas las instancias de Excel mostrando una cuenta regresiva."""
        print("¡Los archivos Excel se cerrarán en 5 segundos!")
        
        for i in range(5, 0, -1):
            print(f"Cerrando en {i}...", end='\r')
            time.sleep(1)
        
        print("\nCerrando Excel...")
        excel_cerrados = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == 'EXCEL.EXE':
                    psutil.Process(proc.info['pid']).terminate()
                    excel_cerrados += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        print(f"Se han cerrado {excel_cerrados} archivo(s) Excel." if excel_cerrados > 0 
              else "No se encontraron instancias de Excel abiertas.")
        print("Continuando con el proceso...")

    def esperar_excel_listo(self, excel, tiempo_max=10):
        inicio = time.time()
        while time.time() - inicio < tiempo_max:
            try:
                if excel.Ready:
                    return True
            except:
                pass
            time.sleep(0.5)
        print("⚠️ Excel no respondió dentro del tiempo esperado.")
        return False

    def refresh_archivo_excel(self):
        self.kill_excel()
        """Actualiza todas las conexiones y tablas dinámicas en el archivo Excel."""
        pythoncom.CoInitialize()
        excel = libro = None
        
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = True
            print(f"📖 Abriendo libro {self.archivo_excel}...")
            libro = excel.Workbooks.Open(self.archivo_excel)
            time.sleep(10)
            self.esperar_excel_listo(excel)
            
            print("🔌 Actualizando conexiones...")
            libro.RefreshAll()
            excel.CalculateUntilAsyncQueriesDone()
            print("✅ Actualización de datos completada")
            
            time.sleep(3)
            
            print("📊 Actualizando tablas dinámicas...")
            for hoja in libro.Sheets:
                try:
                    for pt in hoja.PivotTables():
                        pt.RefreshTable()
                except:
                    continue
            print("✅ Tablas dinámicas actualizadas")
            
            time.sleep(3)

            # -- Retornar ambos objetos -- 
            return excel, libro
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise


    def exportar_imagenes_excel(self, excel, libro):
        print("\n📸 Iniciando captura de imágenes...")

        try:
            for captura_img in self.var_captura_img:
                intentos = 0
                exito = False

                while intentos < 3 and not exito:
                    try:
                        print(f"🌀 Intento {intentos + 1} para hoja: {captura_img['hojas_captura_img']}")
                        
                        excel.CalculateUntilAsyncQueriesDone()
                        hoja = libro.Worksheets(captura_img['hojas_captura_img'])
                        hoja.Activate()

                        self.esperar_excel_listo(excel)
                        time.sleep(5)

                        excel.CalculateUntilAsyncQueriesDone()
                        print(f"Capturando {captura_img['rangos_captura_img']} de {captura_img['hojas_captura_img']}")

                        rango = hoja.Range(captura_img['rangos_captura_img'])
                        rango.CopyPicture(Format=2)
                        time.sleep(5)

                        img = None
                        for _ in range(3):
                            img = ImageGrab.grabclipboard()
                            if img:
                                break
                            time.sleep(3)

                        if img:
                            img_path = os.path.join(self.ruta_img, f"{captura_img['hojas_captura_img']}.png")
                            img.save(img_path, 'PNG')
                            print(f"✅ Imagen guardada en {img_path}")
                            exito = True  # Marca éxito y rompe el while
                        else:
                            print(f"⚠️ No se pudo capturar imagen (grabclipboard vacía).")

                    except Exception as e:
                        print(f"⚠️ Error en intento {intentos + 1} para {captura_img['hojas_captura_img']}: {str(e)}")

                    intentos += 1

                if not exito:
                    print(f"❌ Fallaron los 3 intentos para capturar {captura_img['hojas_captura_img']}")

        except Exception as e:
            print(f"⚠️ Error general en exportar_imagenes_excel: {str(e)}")


                    
    def copiar_celdas_txt(self, excel, libro):
        warnings.filterwarnings("ignore", category=UserWarning, message=".*extension is not supported.*")

        if not hasattr(self, 'var_captura_img') or not self.var_captura_img:
            print("⚠️ No se han definido hojas para capturar texto")
            return

        for captura_txt in self.var_captura_img:
            try:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.CloseClipboard()
                    print("Limpieza de portapapeles completa, copiando celdas")
                except Exception as e:
                    print(f"⚠️ Error al limpiar el portapapeles: {str(e)}")

                if 'hojas_captura_img' not in captura_txt:
                    print("⚠️ Falta especificar 'hojas_captura_img' en la configuración")
                    continue

                hoja = libro.Worksheets(captura_txt['hojas_captura_img'])
                fila = captura_txt.get('fila', 1) + 1  # --Excel es 1-based --
                columna = captura_txt.get('columna', 0) + 1
                
                valor = hoja.Cells(fila, columna).Value

                if valor:
                    nombre_hoja = captura_txt['hojas_captura_img']
                    nombre_archivo = "".join(c for c in nombre_hoja if c.isalnum() or c in (' ', '_')).rstrip()
                    txt_path = os.path.join(self.ruta_txt, f"{nombre_archivo}.txt")

                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(str(valor))
                    print(f"✅ {nombre_hoja}: Celda {fila},{columna} -> {txt_path}")
                else:
                    print(f"ℹ️ {captura_txt['hojas_captura_img']}: Celda {fila},{columna} está vacía")

            except Exception as e:
                print(f"⚠️ Error procesando {captura_txt.get('hojas_captura_img', 'hoja desconocida')}: {str(e)}")
        
        print("💾 Guardando...")
        libro.Save()
        time.sleep(5)
        libro.Close(SaveChanges=False)
        excel.Quit()
        pythoncom.CoUninitialize()

class Envio_Pdc_Wpp:

    def __init__(self, processor: Process_Excel, tabla_alerta=None, diferencia_minutos=None):
        
        self.profile_path = processor.profile_path
        self.driver_path = processor.driver_path
        self.url = processor.url
        self.ruta_img = processor.ruta_img
        self.ruta_txt = processor.ruta_txt
        self.var_captura_img = processor.var_captura_img
        self.xpath_buscar_chats = processor.xpath_buscar_chats
        self.xpath_boton_adjun = processor.xpath_boton_adjun
        self.xpath_input_img = processor.xpath_input_img
        self.xpath_mensaje = processor.xpath_mensaje
        self.xpath_boton_enviar = processor.xpath_boton_enviar
        self.xpath_wpp = processor.xpath_wpp

    def env_pdc_bot(self):
        try:
            driver = WebScraping_Chrome.Webdriver_ChrPP_DP(self.profile_path, self.driver_path)
            WebScraping_Chrome.WebScraping_Acces(driver, self.url)
            WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_wpp)

            for grupo in tqdm.tqdm(self.var_captura_img):
                try:
                    WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_buscar_chats)
                    WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_buscar_chats)
                    
                    time.sleep(1)
                    
                    WebScraping_Chrome.WebScraping_Cle(driver, self.xpath_buscar_chats)
                    
                    time.sleep(1)
                    
                    WebScraping_Chrome.WebScraping_Keys(driver, self.xpath_buscar_chats, grupo['nombre_grupo'])
                    
                    time.sleep(1)

                    buscador_grupo = f'//span[@title="{grupo["nombre_grupo"]}"]'
                    WebScraping_Chrome.WebScraping_Wait(driver, 120, buscador_grupo)
                    WebScraping_Chrome.WebScraping_Nav(driver, buscador_grupo)

                    time.sleep(1)

                    imagen_path = os.path.join(self.ruta_img, f"{grupo['hojas_captura_img']}.png")
                    if os.path.exists(imagen_path):
                        WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_boton_adjun)
                        WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_boton_adjun)

                        time.sleep(1)

                        WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_input_img)
                        WebScraping_Chrome.WebScraping_Keys(driver, self.xpath_input_img, imagen_path)
                        time.sleep(2)

                    else:
                        print(f"⚠️ La imagen {imagen_path} no se encuentra.")
                        
                    texto_path = os.path.join(self.ruta_txt, f"{grupo['hojas_captura_img']}.txt")
                    if os.path.exists(texto_path):                    
                        with open(texto_path, 'r', encoding='utf-8') as file:
                            texto_a_pegar = file.read()

                            WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_mensaje)
                            WebScraping_Chrome.WebScraping_Keys(driver, self.xpath_mensaje, texto_a_pegar)

                            WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_boton_enviar)
                            WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_boton_enviar)

                            time.sleep(8)
                    else:
                        print(f"⚠️ El archivo de texto {texto_path} no se encuentra.")
                except Exception as e:
                    print(f"⚠️ Error al enviar mensaje al grupo {grupo['nombre_grupo']}: {str(e)}")
        except Exception as e:
            print(f"❌ Error general en el bot: {str(e)}")

class EnvioErrorPdc:

    def __init__(self, tabla_alerta=None, diferencia_minutos=None):
        
        self.path_home = str(Path.home())  # -----> Esto devuelve "C:\Users\tu_usuario"
        self.profile_path = os.path.join(
            self.path_home,
            'AppData',
            'Local',
            'Google',
            'Chrome',
            'User Data',
            'Default',
            'perfil_selenium_1'
        )
        self.driver_path = os.path.join(
            self.path_home,
            'Documents',
            'chromedriver.exe'
        )
        self.url = 'https://web.whatsapp.com/'
        self.xpath_buscar_chats = '//div[@aria-placeholder="Search or start a new chat"]' 
        self.xpath_boton_enviar = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button'
        self.xpath_enviar_mensaje = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/button'
        self.xpath_wpp = '//*[@id="app"]/div/div[3]/div/div[3]/header/header'
        self.xpath_escribir_msj = '//div[@aria-placeholder="Type a message"]'
        self.grupo_alerta = 'Mediciones Data strategies Latam'
        self.tabla_alerta = tabla_alerta 
        self.diferencia_minutos = diferencia_minutos
        self.mensaje_alerta = ( f"Se confirma error: La tabla de marcaciones {self.tabla_alerta} ubicada en el servidor 172.70.7.61 "
                                f"no se ha actualizado en mas de {self.diferencia_minutos} minutos. "
                                f"*Lideres De Data Strategies* Su ayuda escalándolo." 
        )

    def bot_envio_error(self):

            try:
                driver = WebScraping_Chrome.Webdriver_ChrPP_DP(self.profile_path, self.driver_path)
                WebScraping_Chrome.WebScraping_Acces(driver, self.url)
                WebScraping_Chrome.WebScraping_Wait(driver, 500, self.xpath_wpp)

                WebScraping_Chrome.WebScraping_Wait(driver, 120, self.xpath_buscar_chats)
                WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_buscar_chats)      

                WebScraping_Chrome.WebScraping_Cle(driver, self.xpath_buscar_chats)
                            
                WebScraping_Chrome.WebScraping_Keys(driver, self.xpath_buscar_chats, self.grupo_alerta)
                
                time.sleep(1)
                
                buscador_grupo = f'//span[@title="{self.grupo_alerta}"]'
                WebScraping_Chrome.WebScraping_Wait(driver, 120, buscador_grupo)
                WebScraping_Chrome.WebScraping_Nav(driver, buscador_grupo)

                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_escribir_msj)
                WebScraping_Chrome.WebScraping_Cle(driver, self.xpath_escribir_msj)  
                WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_escribir_msj)        
                WebScraping_Chrome.WebScraping_Keys(driver, self.xpath_escribir_msj, self.mensaje_alerta)
                
                time.sleep(3)
                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_enviar_mensaje)
                WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_enviar_mensaje)
                time.sleep(15)

                print(f"✅ Mensaje enviado correctamente al grupo {self.grupo_alerta}")
            except Exception as e:
                print(f"❌ Error al enviar mensaje al grupo {self.grupo_alerta}: {e}")
            finally:
                if driver:
                    driver.quit()