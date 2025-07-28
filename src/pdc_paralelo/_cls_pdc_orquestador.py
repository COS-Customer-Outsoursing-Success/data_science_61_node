# src/pdc_orquestador.py
import os
import sys
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from conexiones_db._cls_sqlalchemy import MySQLConnector
from excel_app._cls_excel_auto_manager import Process_Excel, Envio_Pdc_Wpp, EnvioErrorPdc
from vicidial._cls_scraping_detalle_agente import DetalleAgenteVcdl

class PdcOrquestador:

    def __init__(self, config):
        self.config_campanas = config
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.project_home = os.path.dirname(self.project_root)
        self.path_home = str(Path.home())
        self.excel_lock = Lock()
        self.intentos_max = 5
        self.intervalo_consulta = 300
        self.intervalo_max = 45

    def ejecutar_vcdl_por_campana(self, conf):
        try:
            print(f"📥 Iniciando VCDL: {conf['campana']}")
            processor_detalle_ag = DetalleAgenteVcdl(
                schema=conf["schema"],
                table='tb_detalle_agente_daily_new_dts',
                http_vcdl=conf['http_vcdl'],
                user_vcdl='1031120694',
                pass_vcdl='wfm1031120694',
                server_vcdl=conf["server_vcdl"],
                campanas_vcdl=conf["campanas_vcdl"],
                download_path=os.path.join(self.project_home, 'data', 'detalle_agente', conf["campana"])
            )
            processor_detalle_ag.eliminar_archivos_ruta()
            processor_detalle_ag.descargar_reporte()
            processor_detalle_ag.process_downloaded_file()
            processor_detalle_ag.load_data()
            print(f"✅ Finalizado VCDL: {conf['campana']}")
        except Exception as e:
            print(f"❌ Error VCDL en campaña {conf['campana']}: {str(e)}")

    def ejecutar_excel_por_campana(self, conf, index=0):
        profile_path = os.path.join(self.path_home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data',
                                     'Default', f'perfil_selenium_{index}')
        try:
            print(f"📊 Iniciando Excel: {conf['campana']} con perfil {profile_path}")
            processor_excel = Process_Excel(
                profile_path=profile_path,
                schema=conf["schema"],
                stored_procedures=conf["stored_procedures"],
                archivo_excel=conf["archivo_excel"],
                var_captura_img=conf["var_captura_img"],
                ruta_img=os.path.join(self.project_home, 'data', 'img', 'pdc', conf["campana"]),
                ruta_txt=os.path.join(self.project_home, 'data', 'txt', 'pdc', conf["campana"])
            )
            processor_excel.ejecutar_sps()
            processor_excel.delete_archivos_ruta()
            excel, libro = processor_excel.refresh_archivo_excel()
            processor_excel.exportar_imagenes_excel(excel, libro)
            processor_excel.copiar_celdas_txt(excel, libro)
            return processor_excel
        except Exception as e:
            print(f"❌ Error Excel en campaña {conf['campana']}: {str(e)}")
            return None

    def ejecutar_envio_pdc_por_campana(self, conf, processor_excel):
        try:
            processor_envio_wpp = Envio_Pdc_Wpp(processor_excel)
            processor_envio_wpp.env_pdc_bot()
        except Exception as e:
            print(f"❌ Error en el proceso de envio wpp: {str(e)}")

    def leer_query(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error al leer el archivo SQL: {str(e)}")
            raise

    def env_error(self, conf, index):

        sql_file_path = os.path.join(self.project_home, 'sql', conf["sql_file_name"])
        engine = MySQLConnector().get_connection(database='bbdd_config')
        query_max = self.leer_query(sql_file_path)
        df = pd.read_sql(query_max, engine)

        df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce').fillna(pd.to_datetime('00:00:00'))
        hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
        hora_actual = datetime.now().strftime('%H:%M')

        diferencia_minutos = (
            datetime.strptime(hora_actual, '%H:%M') -
            datetime.strptime(hora_ultima_llamada, '%H:%M')
        ).total_seconds() / 60

        profile_path = os.path.join(self.path_home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data',
                                    'Default', f'perfil_selenium_{index}')
        processor_env_error = EnvioErrorPdc(
            tabla_alerta=conf["tabla_alerta"],
            diferencia_minutos=diferencia_minutos,
            profile_path=profile_path
        )
        try:
            processor_env_error.bot_envio_error()
        except Exception as e:
            print(f"❌ Error en el proceso de envio error wpp: {str(e)}")

    def evaluar_y_ejecutar(self, conf, index):
        for intento in range(self.intentos_max):
            try:
                print(f"\n🌀 Evaluando campaña {conf['campana']} (Intento {intento + 1}/{self.intentos_max})")
                sql_file_path = os.path.join(self.project_home, 'sql', conf["sql_file_name"])
                query_max = self.leer_query(sql_file_path)
                engine = MySQLConnector().get_connection(database='bbdd_config')
                df = pd.read_sql(query_max, engine)

                df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce').fillna(pd.to_datetime('00:00:00'))
                hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
                hora_actual = datetime.now().strftime('%H:%M')

                diferencia_minutos = (
                    datetime.strptime(hora_actual, '%H:%M') -
                    datetime.strptime(hora_ultima_llamada, '%H:%M')
                ).total_seconds() / 60

                if diferencia_minutos < self.intervalo_max:
                    print(f"✅ Ejecutando proceso completo de {conf['campana']}")
                    self.ejecutar_vcdl_por_campana(conf)
                    with self.excel_lock:
                        processor = self.ejecutar_excel_por_campana(conf, index)
                    if processor:
                        self.ejecutar_envio_pdc_por_campana(conf, processor)
                    return
                else:
                    print(f"⏳ No cumple condición. Esperando...")
                    time.sleep(self.intervalo_consulta)

            except Exception as e:
                print(f"❌ Error evaluando campaña {conf['campana']}: {e}")
                time.sleep(self.intervalo_consulta)

        print(f"❌ Máximos intentos alcanzados para {conf['campana']}. Enviando error.")
        self.env_error(conf, index)

    def ejecutar(self):
        with ThreadPoolExecutor(max_workers=len(self.config_campanas)) as executor:
            futures = [executor.submit(self.evaluar_y_ejecutar, conf, idx)
                       for idx, conf in enumerate(self.config_campanas, start=1)]
            for future in as_completed(futures):
                future.result()
