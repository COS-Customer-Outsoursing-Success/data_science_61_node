"""""
Created By David Salcedo
"""""
import win32com.client
import win32clipboard
import warnings
import time
import pythoncom
import glob
import os
import pandas as pd
import tqdm
from PIL import ImageGrab
import threading
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from conexiones_db._cls_sqlalchemy import MySQLConnector

class Process_Excel:
    def __init__(self, archivo_excel=None, var_captura_img=None, ruta_img=None,
                 ruta_txt=None, diferencia_minutos=None, tabla_alerta=None,
                 schema=None, stored_procedures=None):
        self.archivo_excel = archivo_excel
        self.var_captura_img = var_captura_img
        self.ruta_img = ruta_img
        self.ruta_txt = ruta_txt
        os.makedirs(self.ruta_img, exist_ok=True)
        os.makedirs(self.ruta_txt, exist_ok=True)
        self.schema = schema
        self.stored_procedures = stored_procedures or []
        self.parar_sp = threading.Event()
        self.libro_solo_lectura = False

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

    def cerrar_libro_objetivo(self):
        """Cierra únicamente la instancia de Excel que tiene abierto self.archivo_excel,
        sin afectar otros libros que pueda tener abiertos un tercero en la misma máquina."""
        carpeta = os.path.dirname(self.archivo_excel)
        nombre = os.path.basename(self.archivo_excel)
        centinela = os.path.join(carpeta, f"~${nombre}")

        if not os.path.exists(centinela):
            print(f"'{nombre}' no está abierto por nadie. Continuando...")
            return

        print(f"'{nombre}' está abierto. Cerrando esa instancia (sin afectar otros Excel abiertos)...")
        try:
            libro_abierto = win32com.client.GetObject(self.archivo_excel)
            libro_abierto.Close(SaveChanges=False)
            print(f"'{nombre}' cerrado correctamente.")
        except Exception as e:
            print(f"Advertencia: no se pudo cerrar '{nombre}' automáticamente ({e}). "
                  f"Puede estar abierto desde otra máquina (unidad de red); "
                  f"se intentará abrir en modo solo lectura.")

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

    def _com_retry(self, fn, max_intentos=8, pausa=4):
        """Ejecuta fn() reintentando si Excel rechaza la llamada (RPC_E_CALL_REJECTED)."""
        for i in range(max_intentos):
            try:
                return fn()
            except Exception as e:
                codigo = getattr(e, 'hresult', None) or (e.args[0] if e.args else None)
                if codigo == -2147418111:  # RPC_E_CALL_REJECTED
                    if i < max_intentos - 1:
                        print(f"Excel ocupado (RPC_E_CALL_REJECTED), reintentando en {pausa}s... ({i+1}/{max_intentos})")
                        time.sleep(pausa)
                    else:
                        raise
                else:
                    raise

    def refresh_archivo_excel(self):
        self.cerrar_libro_objetivo()
        """Actualiza todas las conexiones y tablas dinámicas en el archivo Excel."""
        pythoncom.CoInitialize()
        excel = libro = None

        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.Visible = False
            excel.ScreenUpdating = False
            print(f"Abriendo libro {self.archivo_excel}...")
            self.libro_solo_lectura = False
            try:
                libro = excel.Workbooks.Open(self.archivo_excel)
            except Exception as e:
                print(f"No se pudo abrir en modo escritura ({e}). Reintentando en solo lectura...")
                libro = excel.Workbooks.Open(
                    self.archivo_excel,
                    ReadOnly=True,
                    UpdateLinks=0,
                    IgnoreReadOnlyRecommended=True
                )
                self.libro_solo_lectura = True
                print("Libro abierto en modo solo lectura (otro usuario/máquina lo tiene abierto).")
            time.sleep(10)
            self.esperar_excel_listo(excel)
            
            print("Actualizando conexiones...")
            # Forzar refresh sincrono para evitar errores con CalculateUntilAsyncQueriesDone
            for conn in libro.Connections:
                try:
                    conn.OLEDBConnection.BackgroundQuery = False
                except Exception:
                    try:
                        conn.ODBCConnection.BackgroundQuery = False
                    except Exception:
                        pass
            for hoja in libro.Sheets:
                try:
                    for qt in hoja.QueryTables:
                        qt.BackgroundQuery = False
                except Exception:
                    continue

            libro.RefreshAll()
            try:
                excel.CalculateUntilAsyncQueriesDone()
            except Exception as e:
                print(f"Advertencia CalculateUntilAsyncQueriesDone: {e}. Esperando 30s...")
                time.sleep(30)
            print("Actualización de datos completada")
            
            time.sleep(3)
            self.esperar_excel_listo(excel, tiempo_max=30)

            print("Actualizando tablas dinámicas...")
            try:
                num_hojas = self._com_retry(lambda: libro.Sheets.Count)
                for i in range(1, num_hojas + 1):
                    try:
                        hoja = self._com_retry(lambda i=i: libro.Sheets(i))
                        pts  = self._com_retry(lambda: hoja.PivotTables())
                        for pt in pts:
                            try:
                                self._com_retry(lambda pt=pt: pt.RefreshTable())
                            except Exception:
                                pass
                    except Exception:
                        continue
            except Exception as e:
                print(f"Advertencia tablas dinámicas: {e}")
            print("Tablas dinámicas actualizadas")
            
            time.sleep(3)

            # -- Retornar ambos objetos -- 
            return excel, libro
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if libro is not None:
                try: libro.Close(SaveChanges=False)
                except: pass
            if excel is not None:
                try: excel.Quit()
                except: pass
            pythoncom.CoUninitialize()
            raise


    def exportar_imagenes_excel(self, excel, libro):
        print("\n Iniciando captura de imágenes...")

        # Excel puede estar ocupado (RPC_E_CALL_REJECTED) justo después del refresh.
        # Reintentar hasta 10 veces con pausa de 3 s antes de continuar.
        for intento_sc in range(10):
            try:
                excel.ScreenUpdating = True
                break
            except Exception:
                if intento_sc < 9:
                    print(f"Excel ocupado, esperando... ({intento_sc + 1}/10)")
                    time.sleep(3)
                else:
                    raise

        time.sleep(8)

        try:
            for captura_img in self.var_captura_img:
                intentos = 0
                exito = False

                while intentos < 5 and not exito:
                    try:
                        print(f"Intento {intentos + 1} para hoja: {captura_img['hojas_captura_img']}")

                        self._com_retry(lambda: excel.CalculateUntilAsyncQueriesDone())
                        hoja = self._com_retry(lambda: libro.Worksheets(captura_img['hojas_captura_img']))
                        self._com_retry(lambda: hoja.Activate())

                        self.esperar_excel_listo(excel, tiempo_max=15)
                        time.sleep(5)

                        self._com_retry(lambda: excel.CalculateUntilAsyncQueriesDone())
                        print(f"Capturando {captura_img['rangos_captura_img']} de {captura_img['hojas_captura_img']}")

                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.CloseClipboard()

                        rango = self._com_retry(lambda: hoja.Range(captura_img['rangos_captura_img']))
                        self._com_retry(lambda: rango.CopyPicture(Format=2))
                        secuencia_tras_copia = win32clipboard.GetClipboardSequenceNumber()

                        img = None
                        for _ in range(3):
                            img = ImageGrab.grabclipboard()
                            if img:
                                break
                            time.sleep(1)

                        if img and win32clipboard.GetClipboardSequenceNumber() != secuencia_tras_copia:
                            print(f"Portapapeles modificado por otro proceso durante la captura de "
                                  f"{captura_img['hojas_captura_img']}. Descartando e reintentando.")
                            img = None

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
                    print(f"Error: Error Fallaron los 5 intentos para capturar {captura_img['hojas_captura_img']}")

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
        
        if getattr(self, 'libro_solo_lectura', False):
            print("Libro abierto en modo solo lectura: se omite el guardado.")
        else:
            try:
                print("Guardando...")
                libro.Save()
            except Exception as e:
                print(f"Error al guardar libro: {e}")

        try: libro.Close(SaveChanges=False)
        except: pass
        try: excel.Quit()
        except: pass
        pythoncom.CoUninitialize()

