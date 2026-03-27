"""""
Created By David Salcedo
"""""
import win32com.client
import win32clipboard
import win32gui
import win32con
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
from selenium.webdriver.common.by import By
import os
import time
import tqdm

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
        self.xpath_boton_adjun = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/button' 
        self.xpath_input_img = ('//input[@type="file" and contains(@accept,"image") ''and contains(@accept,"video")]')
        self.xpath_mensaje = '//div[@aria-placeholder="Add a caption"]'
        self.xpath_boton_enviar = '//*[@id="app"]/div[1]/div/div[3]/div/div[2]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'
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
        print("Advertencia: Excel no respondió dentro del tiempo esperado.")
        return False

    def refresh_archivo_excel(self):
        self.kill_excel()
        """Actualiza todas las conexiones y tablas dinámicas en el archivo Excel."""
        pythoncom.CoInitialize()
        excel = libro = None
        
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = False
            excel.ScreenUpdating = False
            print(f"Abriendo libro {self.archivo_excel}...")
            libro = excel.Workbooks.Open(self.archivo_excel)
            time.sleep(10)
            self.esperar_excel_listo(excel)
            
            print("Actualizando conexiones...")
            libro.RefreshAll()
            excel.CalculateUntilAsyncQueriesDone()
            print("Actualización de datos completada")
            
            time.sleep(3)
            
            print("Actualizando tablas dinámicas...")
            for hoja in libro.Sheets:
                try:
                    for pt in hoja.PivotTables():
                        pt.RefreshTable()
                except:
                    continue
            print("Tablas dinámicas actualizadas")
            
            time.sleep(3)

            # -- Retornar ambos objetos -- 
            return excel, libro
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise


    def exportar_imagenes_excel(self, excel, libro):
        print("\n Iniciando captura de imágenes...")
        excel.ScreenUpdating = True
        time.sleep(2)

        try:
            for captura_img in self.var_captura_img:
                intentos = 0
                exito = False

                while intentos < 3 and not exito:
                    try:
                        print(f"Intento {intentos + 1} para hoja: {captura_img['hojas_captura_img']}")
                        
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
                            from PIL import Image

                            img = img.convert("RGB")

                            bg = Image.new("RGB", img.size, (255, 255, 255))
                            bg.paste(img)
                            img = bg

                            min_width = 1200
                            min_height = 700

                            if img.width < min_width or img.height < min_height:
                                scale_w = min_width / img.width
                                scale_h = min_height / img.height
                                scale = max(scale_w, scale_h)

                                img = img.resize(
                                    (int(img.width * scale), int(img.height * scale)),
                                    Image.Resampling.LANCZOS
                                )

                            img_path = os.path.join(
                                self.ruta_img,
                                f"{captura_img['hojas_captura_img']}.jpg"
                            )

                            img.save(
                                img_path,
                                "JPEG",
                                quality=88,
                                subsampling=2,
                                dpi=(96, 96), 
                                optimize=True
                            )

                            peso_kb = round(os.path.getsize(img_path) / 1024, 2)
                            print(f"Imagen lista para WhatsApp: {img_path} | {img.size} | {peso_kb} KB")

                            exito = True

                        else:
                            print(f"Error: Error No se pudo capturar imagen (grabclipboard vacía).")

                    except Exception as e:
                        print(f"Error: Error en intento {intentos + 1} para {captura_img['hojas_captura_img']}: {str(e)}")

                    intentos += 1

                if not exito:
                    print(f"Error: Error Fallaron los 3 intentos para capturar {captura_img['hojas_captura_img']}")

        except Exception as e:
            print(f"Error: Error general en exportar_imagenes_excel: {str(e)}")


                    
    def copiar_celdas_txt(self, excel, libro):
        warnings.filterwarnings("ignore", category=UserWarning, message=".*extension is not supported.*")

        if not hasattr(self, 'var_captura_img') or not self.var_captura_img:
            print("Advertencia: No se han definido hojas para capturar texto")
            return

        for captura_txt in self.var_captura_img:
            try:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.CloseClipboard()
                    print("Limpieza de portapapeles completa, copiando celdas")
                except Exception as e:
                    print(f"Error: Error al limpiar el portapapeles: {str(e)}")

                if 'hojas_captura_img' not in captura_txt:
                    print("Error: Falta especificar 'hojas_captura_img' en la configuración")
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
                print(f"Error: Error procesando {captura_txt.get('hojas_captura_img', 'hoja desconocida')}: {str(e)}")
        
        print("Guardando...")
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
        self.xpath_boton_adjun = processor.xpath_boton_adjun
        self.xpath_input_img = processor.xpath_input_img
        self.xpath_mensaje = processor.xpath_mensaje
        self.xpath_boton_enviar = processor.xpath_boton_enviar
        self.xpath_wpp = processor.xpath_wpp

    def env_pdc_bot(self):
        try:
            driver = WebScraping_Chrome.Webdriver_ChrPP_DP(
                self.profile_path,
                self.driver_path
            )
            WebScraping_Chrome.WebScraping_Acces(driver, self.url)
    
            search_box_selector_texto_img = (
                'div[role="textbox"][aria-placeholder="Escribe un mensaje"], '
                'div[role="textbox"][aria-placeholder="Type a message"], '
                'div[role="textbox"][aria-placeholder="Message"], '
                'div[role="textbox"][aria-placeholder="Mensaje"], '
                'p[role="textbox"][aria-placeholder="Escribe un mensaje"], '
                'p[role="textbox"][aria-placeholder="Type a message"], '
                'footer div[role="textbox"], '
                'footer p[role="textbox"]'
            )

            send_button_selector_envio = (
                'div[role="button"][aria-label="Send"], '
                'div[role="button"][aria-label="Enviar"]'
            )

            print("Esperando que cargue WhatsApp Web...")
            WebScraping_Chrome.WebScraping_WaitCSS(driver, 300, '#app, #startup')
            print("WhatsApp cargado. Esperando que el UI se renderice completamente...")
            WebScraping_Chrome.WebScraping_WaitCSS(driver, 60, 'input[placeholder]')
            print("Detectando selector del buscador...")

            info_buscador = driver.execute_script("""
                var candidatos = [
                    'div[role="textbox"][aria-placeholder]',
                    'p[role="textbox"][aria-placeholder]',
                    'input[placeholder]',
                    'div[contenteditable="true"]',
                    'p[contenteditable="true"]'
                ];
                for (var i = 0; i < candidatos.length; i++) {
                    var els = document.querySelectorAll(candidatos[i]);
                    for (var j = 0; j < els.length; j++) {
                        var ph = (els[j].getAttribute('aria-placeholder') || els[j].getAttribute('placeholder') || '').toLowerCase();
                        if (ph.includes('buscar') || ph.includes('search')) {
                            return {selector: candidatos[i], placeholder: ph, tag: els[j].tagName};
                        }
                    }
                }
                return null;
            """)

            if info_buscador:
                search_box_selector_grupo = info_buscador['selector']
                print(f"Buscador detectado: tag={info_buscador['tag']} selector={search_box_selector_grupo} placeholder='{info_buscador['placeholder']}'")
            else:
                search_box_selector_grupo = (
                    'div[role="textbox"][aria-placeholder="Buscar un chat o iniciar uno nuevo"], '
                    'div[role="textbox"][aria-placeholder="Search or start a new chat"], '
                    'div[role="textbox"][aria-placeholder="Buscar"], '
                    'div[role="textbox"][aria-placeholder="Search"], '
                    'p[role="textbox"][aria-placeholder="Buscar un chat o iniciar uno nuevo"], '
                    'p[role="textbox"][aria-placeholder="Search or start a new chat"], '
                    'p[role="textbox"][aria-placeholder="Buscar"], '
                    'p[role="textbox"][aria-placeholder="Search"]'
                )
                print("Buscador no detectado via JS, usando fallback múltiple.")

            print("Buscador de grupos listo. Iniciando envíos...")
    
            for grupo in tqdm.tqdm(self.var_captura_img):
            
                try:
                    # -------------------- BUSCAR GRUPO --------------------
                    print(f"\n[GRUPO] Buscando: {grupo['nombre_grupo']}")
                    WebScraping_Chrome.WebScraping_ClearCSS(driver, search_box_selector_grupo)
                    WebScraping_Chrome.WebScraping_ClickCSS(driver, search_box_selector_grupo)
                    time.sleep(0.3)

                    WebScraping_Chrome.WebScraping_SendKeysCSS(
                        driver,
                        search_box_selector_grupo,
                        grupo['nombre_grupo']
                    )
                    print(f"[GRUPO] Texto enviado al buscador, esperando span...")
                    time.sleep(1)

                    buscador_grupo = f'//span[@title="{grupo["nombre_grupo"]}"]'
                    WebScraping_Chrome.WebScraping_Wait(driver, 60, buscador_grupo)
                    WebScraping_Chrome.WebScraping_Nav(driver, buscador_grupo)
                    print(f"[GRUPO] Click en grupo realizado.")
                    time.sleep(1)
    
                    # -------------------- ADJUNTAR IMAGEN --------------------
                    imagen_path = os.path.join(
                        self.ruta_img,
                        f"{grupo['hojas_captura_img']}.jpg"
                    )
    
                    # Debug: Verificar tamaño de imagen
                    if os.path.exists(imagen_path):
                        from PIL import Image
                        img_info = Image.open(imagen_path)
                        size_kb = os.path.getsize(imagen_path) / 1024
                        print(f"📸 Imagen: {img_info.size}, {size_kb:.1f}KB")
                        
                        # WhatsApp considera sticker si es muy pequeña o cuadrada
                        if img_info.width < 500 or img_info.height < 500:
                            print("⚠️ ADVERTENCIA: Imagen muy pequeña, puede enviarse como sticker")
                        if abs(img_info.width - img_info.height) < 100:
                            print("⚠️ ADVERTENCIA: Imagen casi cuadrada, puede enviarse como sticker")
    
                    if os.path.exists(imagen_path):
                        try:
                            # 1️⃣ Click en el clip (adjuntar) para abrir el menú de adjuntos
                            clip_xpath = '//*[@id="main"]/footer//span/button'
                            WebScraping_Chrome.WebScraping_Wait(driver, 15, clip_xpath)
                            WebScraping_Chrome.WebScraping_Nav(driver, clip_xpath)
                            time.sleep(0.8)

                            # 2️⃣ Hilo que OCULTA el diálogo del OS sin cerrarlo (SW_HIDE)
                            # WM_CLOSE = "Cancelar" → WhatsApp resetea estado → sticker
                            # SW_HIDE = invisible pero abierto → WhatsApp conserva estado de foto
                            def _ocultar_dialogo_os(timeout=5):
                                titulos = ["Abrir", "Open"]
                                deadline = time.time() + timeout
                                while time.time() < deadline:
                                    for titulo in titulos:
                                        hwnd = win32gui.FindWindow(None, titulo)
                                        if hwnd:
                                            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                                            return
                                    time.sleep(0.01)

                            # 3️⃣ Click en "Fotos y videos" — diálogo se oculta en ~10ms
                            foto_button_selectors = [
                                '//li[@data-tab="1"]',
                                '//button[@aria-label="Photos & videos"]',
                                '//button[@aria-label="Fotos y videos"]',
                                '//span[contains(text(),"Fotos y videos")]/..',
                                '//span[contains(text(),"Photos & videos")]/..',
                            ]
                            for selector in foto_button_selectors:
                                try:
                                    foto_btn = driver.find_element(By.XPATH, selector)
                                    t_dialogo = threading.Thread(target=_ocultar_dialogo_os, args=(5,), daemon=True)
                                    t_dialogo.start()
                                    driver.execute_script("arguments[0].click();", foto_btn)
                                    t_dialogo.join(timeout=6)
                                    print("✅ Click en botón 'Fotos y videos' (diálogo ocultado)")
                                    time.sleep(0.3)
                                    break
                                except Exception:
                                    continue

                            # 4️⃣ Enviar el archivo via send_keys — WhatsApp tiene estado de foto activo
                            inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')
                            attached = False

                            for inp in inputs:
                                try:
                                    accept = inp.get_attribute('accept') or ''
                                    if 'video/mp4' in accept and 'image/*' in accept:
                                        driver.execute_script(
                                            "arguments[0].style.display='block';"
                                            "arguments[0].style.visibility='visible';"
                                            "arguments[0].style.position='absolute';",
                                            inp
                                        )
                                        time.sleep(0.3)
                                        inp.send_keys(imagen_path)
                                        attached = True
                                        print(f"✅ Imagen enviada al input de FOTOS (accept='{accept[:50]}...')")
                                        break
                                except Exception:
                                    continue

                            # Fallback: input genérico de imágenes
                            if not attached:
                                for inp in inputs:
                                    try:
                                        accept = inp.get_attribute('accept') or ''
                                        if 'image/*' in accept and 'webp' not in accept:
                                            driver.execute_script(
                                                "arguments[0].style.display='block';"
                                                "arguments[0].style.visibility='visible';",
                                                inp
                                            )
                                            inp.send_keys(imagen_path)
                                            attached = True
                                            print(f"✅ Imagen enviada (fallback - accept='{accept}')")
                                            break
                                    except Exception:
                                        continue

                            if not attached:
                                print("❌ No se encontró input válido para adjuntar imagen")

                            # 5️⃣ Cerrar el diálogo oculto DESPUÉS de que send_keys ya procesó el archivo
                            for titulo in ["Abrir", "Open"]:
                                hwnd = win32gui.FindWindow(None, titulo)
                                if hwnd:
                                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                                    break

                            time.sleep(2)

                        except Exception as e:
                            print(f"❌ Error general al adjuntar imagen: {e}")
    
                    else:
                        print(f"❌ Imagen no encontrada: {imagen_path}")
    
                    # -------------------- TEXTO --------------------
                    texto_path = os.path.join(
                        self.ruta_txt,
                        f"{grupo['hojas_captura_img']}.txt"
                    )
    
                    if os.path.exists(texto_path):
                    
                        with open(texto_path, 'r', encoding='utf-8') as f:
                            texto = f.read()
    
                        WebScraping_Chrome.WebScraping_WaitCSS(
                            driver,
                            60,
                            search_box_selector_texto_img
                        )
    
                        WebScraping_Chrome.WebScraping_SendKeysCSS(
                            driver,
                            search_box_selector_texto_img,
                            texto
                        )
                        time.sleep(1)
    
                        WebScraping_Chrome.WebScraping_WaitCSS(
                            driver,
                            30,
                            send_button_selector_envio
                        )
                        WebScraping_Chrome.WebScraping_ClickCSS(
                            driver,
                            send_button_selector_envio
                        )
    
                        time.sleep(3)

                    else:
                        print(f"❌ Texto no encontrado: {texto_path}")
    
                except Exception as e:
                    print(f"❌ Error grupo {grupo['nombre_grupo']}: {e}")
    
        except Exception as e:
            print(f"❌ Error general del bot: {e}")

class EnvioErrorPdc:

    def __init__(self, tabla_alerta=None, diferencia_minutos=None, profile_path=None):
        
        self.path_home = str(Path.home())  # -----> Esto devuelve "C:\Users\tu_usuario"
        self.profile_path = profile_path

        self.driver_path = os.path.join(
            self.path_home,
            'Documents',
            'chromedriver.exe'
        )
        self.url = 'https://web.whatsapp.com/'
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

                WebScraping_Chrome.WebScraping_WaitCSS(driver, 120, 'div[contenteditable="true"][role="textbox"]')
                WebScraping_Chrome.WebScraping_ScrollIntoViewCSS(driver, 'div[contenteditable="true"][role="textbox"]')

                WebScraping_Chrome.WebScraping_ClickCSS(driver, 'div[contenteditable="true"][role="textbox"]')

                WebScraping_Chrome.WebScraping_SendKeysCSS(driver, 'div[contenteditable="true"][role="textbox"]', self.grupo_alerta)

                
                time.sleep(1)
                
                buscador_grupo = f'//span[@title="{self.grupo_alerta}"]'
                WebScraping_Chrome.WebScraping_Wait(driver, 120, buscador_grupo)
                WebScraping_Chrome.WebScraping_Nav(driver, buscador_grupo)
                                
                WebScraping_Chrome.WebScraping_WaitCSS(driver, 120, "footer div[role='textbox'][contenteditable='true']")

                WebScraping_Chrome.WebScraping_ScrollIntoViewCSS(driver, "footer div[role='textbox'][contenteditable='true']")

                WebScraping_Chrome.WebScraping_ClickCSS(driver, "footer div[role='textbox'][contenteditable='true']")

                WebScraping_Chrome.WebScraping_SendKeysCSS(driver, "footer div[role='textbox'][contenteditable='true']", self.mensaje_alerta)
                
                time.sleep(3)
                
                WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_enviar_mensaje)
                WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_enviar_mensaje)
                time.sleep(30)

                print(f"Mensaje enviado correctamente al grupo {self.grupo_alerta}")
            except Exception as e:
                print(f"Error: Error al enviar mensaje al grupo {self.grupo_alerta}: {e}")
            finally:
                if driver:
                    driver.quit()