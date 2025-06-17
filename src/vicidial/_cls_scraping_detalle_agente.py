# -- coding: utf-8 --
"""
@Author: Emerson.Aguilar
"""
import os
import time
import glob
from pathlib import Path
import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from load_data._cls_load_data import *
from conexiones_db._cls_sqlalchemy import MySQLConnector
from web_scraping._cls_webscraping import WebScraping_Chrome

class DetalleAgenteVcdl:
    def __init__(self, current_folder=None, project_root=None, user_vcdl=None, pass_vcdl=None, 
                 server_vcdl=None, campanas_vcdl=None, download_path=None, schema=None, table=None):
        
        self.current_folder = current_folder 
        self.project_root = project_root
        self.path_home = str(Path.home())  # -----> "C:\Users\tu_usuario"
        self.user_vcdl = user_vcdl
        self.pass_vcdl = pass_vcdl
        self.server_vcdl = server_vcdl
        self.campanas_vcdl = campanas_vcdl or []
        self.url_vcdl = f'http://{self.user_vcdl}:{self.pass_vcdl}@{self.server_vcdl}/vicidial/AST_agent_time_detail.php'
        self.download_path = download_path
        self.rutas_eliminar = [download_path] if download_path else []
        os.makedirs(self.download_path, exist_ok=True)
        self.driver_path = os.path.join(
            self.path_home, 
            'Documents',
            'chromedriver.exe'
        )
        self.schema = schema
        self.table = table 
        self.engine = MySQLConnector().get_connection(database=self.schema) if schema else None
        self.xpath_campanas = '//*[@id="vicidial_report"]/table/tbody/tr/td[2]/select'
        self.xpath_grupos_usuario = '//*[@id="vicidial_report"]/table/tbody/tr/td[3]/select/option[1]'
        self.xpath_remitir = '//*[@id="vicidial_report"]/table/tbody/tr/td[5]/input'
        self.xpath_descargar = '//*[@id="vicidial_report"]/table/tbody/tr/td[6]/font/a[1]'
        self.xpath_wpp = '//*[@id="vicidial_report"]/table/tbody/tr/td[1]/input[1]'
        self.loader = MySQLLoader(self.engine,self.schema,self.table)
 
    def eliminar_archivos_ruta(self):

        try:
            for ruta in self.rutas_eliminar:
                if os.path.exists(ruta):
                    for archivo in glob.glob(os.path.join(ruta, '*')):
                        try:
                            os.remove(archivo)
                            print(f'Archivo eliminado: {archivo}')
                        except Exception as e:
                            print(f'Error al eliminar {archivo}: {e}')
        except Exception as e:
            print(f'Error general al eliminar archivos: {e}')

    def remove_existing_files(self):

        for filename in os.listdir(self.download_path):
            file_path = os.path.join(self.download_path, filename)
            try:
                if os.path.isfile(file_path) and not filename.endswith('.crdownload'):
                    os.remove(file_path)
                    print(f"Archivo eliminado: {filename}")
            except Exception as e:
                print(f"Error eliminando {filename}: {e}")

    def descargar_reporte(self):

        if not all([self.user_vcdl, self.pass_vcdl, self.server_vcdl]):
            raise ValueError("Missing VCDL credentials")
            
        driver = WebScraping_Chrome.Webdriver_ChrDP_DP(self.driver_path, self.download_path)

        try:
            WebScraping_Chrome.WebScraping_Acces(driver, self.url_vcdl)
            WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_campanas)

            WebScraping_Chrome.WebScraping_Wait_Clickeable(driver, 150, self.xpath_campanas)
            WebScraping_Chrome.WebScraping_Select_Xpath(driver, self.xpath_campanas, self.campanas_vcdl)
            print(f"Campañas {self.campanas_vcdl} seleccionadas")
            
            WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_grupos_usuario)
            WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_grupos_usuario)
            print("Grupos de usuario seleccionados")

            WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_remitir)
            WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_remitir)
            print("Consultado informacion detalle agente")
            
            self.remove_existing_files()
            
            WebScraping_Chrome.WebScraping_Wait(driver, 150, self.xpath_descargar)
            WebScraping_Chrome.WebScraping_Nav(driver, self.xpath_descargar)
            print("Descargando detalle agente, esperando descarga completa...")     

            timeout = 200
            start_time = time.time()
            while time.time() - start_time < timeout:
                if any(f.endswith('.csv') for f in os.listdir(self.download_path)):
                    print("Descarga completada.")
                    self.process_downloaded_file()
                    return True
                time.sleep(2)
            
            raise TimeoutError("No se encontró el archivo descargado después del tiempo de espera")
            
        except TimeoutException as te:
            print(f"Error: Tiempo de espera agotado - {te}")
            return False
        except Exception as e:
            print(f"Error inesperado durante la descarga: {e}")
            return False
        finally:
            try:
                driver.quit()
                print("Driver cerrado.")
            except Exception as e:
                print(f"Error al cerrar el driver: {e}")

    def process_downloaded_file(self):
        required_columns = [
            'usuario', 'identificacion', 'llamadas', 'hora', 't_login_time', 
            't_espera', 't_charla', 't_dispo', 't_pausa', 't_llamada_muerta',
            't_customer', 't_connected', 't_almuerzo', 't_back', 't_preturno',
            't_bano', 't_break', 't_chat', 't_capacitacion', 't_venta',
            't_coach', 't_feedback', 't_fallt', 't_email', 't_lagged', 
            't_llms', 't_login', 't_pausa_activa', 't_pausa_productiva', 
            't_visible_vcdl', 't_hiiden_vcdl', 't_video_llamada', 't_whatsapp',
            'fecha_cargue'
        ]
        
        for filename in os.listdir(self.download_path):
            if filename.endswith('.csv'):
                csv_file_path = os.path.join(self.download_path, filename)
                
                timeout = 120
                start_time = time.time()
                while os.path.exists(csv_file_path + ".crdownload"):
                    if time.time() - start_time > timeout:
                        raise TimeoutError("File download timed out")
                    time.sleep(3)
                
                try:

                    df_vcdl = pd.read_csv(csv_file_path, delimiter=',', skiprows=3, encoding='utf-8', 
                      on_bad_lines='warn') 
                    df_vcdl.columns = df_vcdl.columns.str.strip().str.upper()

                    
                    rename_dict = {
                        'USER': 'usuario',
                        'ID': 'identificacion',
                        'CALLS': 'llamadas',
                        'TIME CLOCK': 'hora',
                        'LOGIN TIME': 't_login_time',
                        'WAIT': 't_espera',
                        'TALK': 't_charla',
                        'DISPO': 't_dispo',
                        'PAUSE': 't_pausa',
                        'DEAD': 't_llamada_muerta',
                        'CUSTOMER': 't_customer',
                        'CONNECTED': 't_connected',
                        'ALMU': 't_almuerzo',
                        'BACK': 't_back',
                        'BANO': 't_bano',
                        'BREAK': 't_break',
                        'CAPA': 't_capacitacion',
                        'VENTA': 't_venta',
                        'CHAT': 't_chat',
                        'EMAIL': 't_email',
                        'COACH': 't_coach',
                        'FALLT': 't_fallt',
                        'FEED': 't_feedback',
                        'LAGGED': 't_lagged',
                        'LLMS': 't_llms',
                        'LOGIN': 't_login',
                        'PAC': 't_pausa_activa',
                        'PAPRO': 't_pausa_productiva',
                        'PRETU': 't_preturno',
                        'VISIBLE': 't_visible_vcdl',
                        'HIDDEN': 't_hiiden_vcdl',
                        'VILLA': 't_video_llamada',
                        'WHAT': 't_whatsapp'            
                    }
                    df_vcdl.rename(columns=rename_dict, inplace=True)
                    
                    df_vcdl['fecha_cargue'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                    df_vcdl = df_vcdl.fillna(0)
                    for col in required_columns:
                        if col not in df_vcdl.columns:
                            df_vcdl[col] = 0  
                            print(f"Columna '{col}' no encontrada. Rellenando con valor 0.")

                    self.df = df_vcdl[required_columns]
                    print(f"Procesado archivo: {filename}")
                    print(f"Columnas seleccionadas para la carga: {self.df.columns}")
                    return True
                    
                except Exception as e:
                    print(f"Error procesando archivo {filename}: {e}")
                    continue
        
        print("No se encontraron archivos CSV válidos para procesar")
        return False

    def load_data(self):
        if not hasattr(self, 'df') or self.df.empty:
            print('No data to load')
            return False
            
        if not self.loader:
            print('Database loader not initialized')
            return False
            
        try:
            self.loader.upsert_into_table(self.df)
            print('Load document completed')
            return True
        except Exception as e:
            print(f'Error loading data: {e}')
            return False