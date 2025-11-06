"""
Created By Emerson Aguilar Cruz
"""

import os
import sys
import pandas as pd
import time
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from excel_app._cls_excel_auto_manager import Process_Excel, Envio_Pdc_Wpp, EnvioErrorPdc
from vicidial._cls_scraping_detalle_agente import DetalleAgenteVcdl
from conexiones_db._cls_sqlalchemy import MySQLConnector

config_path = os.path.join(project_root, 'config', 'config_pdc.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

parametro_num_day = 1
path_home = str(Path.home())

def ejecutar_vcdl_por_campana(conf):

    try:
        print(f"📥 Iniciando VCDL: {conf['campana']}")
        processor_detalle_ag = DetalleAgenteVcdl(
            schema=conf["schema"], 
            table='tb_detalle_agente_daily_new_dts',
            http_vcdl = conf['http_vcdl'],
            user_vcdl='1014248469',
            pass_vcdl=conf['pass_vcdl'],
            server_vcdl=conf["server_vcdl"],
            campanas_vcdl=conf["campanas_vcdl"],
            download_path=os.path.join(project_root, 'data', 'detalle_agente', conf["campana"])
        )
        processor_detalle_ag.eliminar_archivos_ruta()
        processor_detalle_ag.descargar_reporte()
        processor_detalle_ag.process_downloaded_file()
        processor_detalle_ag.load_data()
        print(f"✅ Finalizado VCDL: {conf['campana']}")
    except Exception as e:
        print(f"❌ Error VCDL en campaña {conf['campana']}: {str(e)}")

def ejecutar_excel_por_campana(conf, index=0):
    profile_path = os.path.join(
        path_home,
        'AppData',
        'Local',
        'Google',
        'Chrome',
        'User Data',
        f'Default',
        f'perfil_selenium_{index}'
#        f'perfil_selenium_4'
    )
    try:
        print(f"Iniciando Excel: {conf['campana']} con perfil {profile_path}")
        
        processor_excel = Process_Excel(
            profile_path=profile_path,
            schema=conf["schema"],
            stored_procedures=conf["stored_procedures"],
            archivo_excel=conf["archivo_excel"],
            var_captura_img=conf["var_captura_img"],
            ruta_img=os.path.join(project_root, 'data', 'img', 'pdc', conf["campana"]),
            ruta_txt=os.path.join(project_root, 'data', 'txt', 'pdc', conf["campana"])
        )

        processor_excel.ejecutar_sps()
        processor_excel.delete_archivos_ruta()
        excel, libro = processor_excel.refresh_archivo_excel()
        processor_excel.exportar_imagenes_excel(excel, libro)
        processor_excel.copiar_celdas_txt(excel, libro)
        return processor_excel

    except Exception as e:
        print(f"Error: Error Excel en campaña {conf['campana']}: {str(e)}")
        return None

def ejecutar_envio_pdc_por_campana(conf, processor_excel):

    processor_envio_wpp = Envio_Pdc_Wpp(processor_excel)
    try:
        processor_envio_wpp.env_pdc_bot()
    except Exception as e:
        print(f"Error: Error en el proceso de envio wpp: {str(e)}")

def leer_query(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo en {path}")
        raise
    except Exception as e:
        print(f"Error al leer el archivo SQL: {str(e)}")
        raise

def main_multi():

#    config_campanas = [config["config_pdc_chubb"]]
    config_campanas = [config["config_pdc_carteras_bogotá", config["config_pdc_carteras_medellin"]]]

    print("🚀 Ejecutando VCDL en paralelo...")
    with ThreadPoolExecutor(max_workers=len(config_campanas)) as executor:
        futures = [executor.submit(ejecutar_vcdl_por_campana, conf) for conf in config_campanas]
        for future in as_completed(futures):
            future.result()

    print("📊 Ejecutando Excel en secuencia...")
    processors_excel = []
    for idx, conf in enumerate(config_campanas, start=1):
        processor = ejecutar_excel_por_campana(conf, idx)
        processors_excel.append((conf, processor))

    print("🚀 Ejecutando ENVIO PDC en paralelo...")
    with ThreadPoolExecutor(max_workers=len(processors_excel)) as executor:
        futures = [executor.submit(ejecutar_envio_pdc_por_campana, conf, processor)
                   for conf, processor in processors_excel]
        for future in as_completed(futures):
            future.result()

def env_error(conf, index):
    sql_file_path = os.path.join(project_root, 'sql', conf["sql_file_name"])
    tabla_alerta = conf["tabla_alerta"]
    profile_path = os.path.join(
        path_home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default',
        f'perfil_selenium_{index}'
    )

    engine = MySQLConnector().get_connection(database='bbdd_config')
    print("Consultando maxima hora de actualizacion")
    query_max = leer_query(sql_file_path)
    print(f"Consulta leída, ejecutando...")

    df = pd.read_sql(query_max, engine)
    df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce')
    df['hora_ultima_llamada'] = df['hora_ultima_llamada'].fillna(pd.to_datetime('00:00:00'))

    hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
    hora_actual = datetime.now().strftime('%H:%M')

    hora_ultima = datetime.strptime(hora_ultima_llamada, '%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual, '%H:%M')
    diferencia_minutos = (hora_actual_obj - hora_ultima).total_seconds() / 60

    print(f"Hora última llamada: {hora_ultima_llamada}")
    print(f"Hora actual: {hora_actual}")
    print(f"Diferencia en minutos: {diferencia_minutos:.2f}")

    processor_env_error = EnvioErrorPdc(
        tabla_alerta=tabla_alerta,
        diferencia_minutos=diferencia_minutos,
        profile_path=profile_path
    )

    try:
        processor_env_error.bot_envio_error()
    except Exception as e:
        print(f"Error: Error en el proceso de envio wpp: {str(e)}")

excel_lock = Lock()
if __name__ == '__main__':

#    config_campanas = [config["config_pdc_chubb"]]
    config_campanas = [config["config_pdc_carteras_bogotá"], config["config_pdc_carteras_medellin"]]
    
    campañas_a_ejecutar = []
    campañas_fallidas = []
    lock = Lock()

    intentos_max = 5
    intervalo_consulta = 300
    intervalo_max = 50

    def evaluar_y_ejecutar(conf, index):
        intentos = 0
        while intentos < intentos_max:
            try:
                print(f"\n Evaluando campaña {conf['campana']} (Intento {intentos + 1}/{intentos_max})")

                sql_file_path = os.path.join(project_root, 'sql', conf["sql_file_name"])
                query_max = leer_query(sql_file_path)

                engine = MySQLConnector().get_connection(database='bbdd_config')
                df = pd.read_sql(query_max, engine)

 
                df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce')
                df['hora_ultima_llamada'] = df['hora_ultima_llamada'].fillna(pd.to_datetime('00:00:00'))

                hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
                hora_actual = datetime.now().strftime('%H:%M')

                hora_ultima = datetime.strptime(hora_ultima_llamada, '%H:%M')
                hora_actual_obj = datetime.strptime(hora_actual, '%H:%M')
                diferencia_minutos = (hora_actual_obj - hora_ultima).total_seconds() / 60

                print(f"--- Última llamada: {hora_ultima_llamada}")
                print(f"--- Hora actual: {hora_actual}")
                print(f"--- Diferencia: {diferencia_minutos:.2f} minutos")

                if diferencia_minutos < intervalo_max:
                    print(f"Campaña {conf['campana']} cumple condición. Ejecutando proceso completo.")
                    ejecutar_vcdl_por_campana(conf)
                    with excel_lock:
                        processor = ejecutar_excel_por_campana(conf, index)
                    if processor:
                        ejecutar_envio_pdc_por_campana(conf, processor)

                    return
                else:
                    print(f"Campaña {conf['campana']} no cumple. Esperando {intervalo_consulta / 60:.2f} minutos...")
                    intentos += 1
                    time.sleep(intervalo_consulta)

            except Exception as e:
                print(f"Error: Error evaluando campaña {conf['campana']}: {e}")
                intentos += 1
                time.sleep(intervalo_consulta)

        print(f"Error: Error Máximos intentos alcanzados para campaña {conf['campana']}. Enviando error.")
        env_error(conf, index)


    with ThreadPoolExecutor(max_workers=len(config_campanas)) as executor:
        futures = [
            executor.submit(evaluar_y_ejecutar, conf, idx)
            for idx, conf in enumerate(config_campanas, start=1)
        ]
        for future in as_completed(futures):
            future.result()

    if campañas_a_ejecutar:
        print("\n Error: Ejecutando campañas que cumplieron...")

        def main_multi_filtrado(campañas_filtradas):
            with ThreadPoolExecutor(max_workers=len(campañas_filtradas)) as executor:
                futures = [executor.submit(ejecutar_vcdl_por_campana, conf) for conf in campañas_filtradas]
                for future in as_completed(futures):
                    future.result()

            processors_excel = []
            for idx, conf in enumerate(campañas_filtradas, start=1):
                processor = ejecutar_excel_por_campana(conf, idx)
                processors_excel.append((conf, processor))

            with ThreadPoolExecutor(max_workers=len(processors_excel)) as executor:
                futures = [executor.submit(ejecutar_envio_pdc_por_campana, conf, processor)
                           for conf, processor in processors_excel]
                for future in as_completed(futures):
                    future.result()

        main_multi_filtrado(campañas_a_ejecutar)
    else:
        print("\n Error: Error Ninguna campaña cumplió con el tiempo requerido tras los intentos.")

    if campañas_fallidas:
        print("\n Error: Error Ejecutando envíos de error para campañas fallidas...")
        with ThreadPoolExecutor(max_workers=len(campañas_fallidas)) as executor:
            futures = [executor.submit(env_error, conf, idx)
                    for idx, conf in enumerate(campañas_fallidas, start=1)]
            for future in as_completed(futures):
                future.result()