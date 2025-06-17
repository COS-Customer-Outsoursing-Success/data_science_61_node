"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys
import pandas as pd
import time
from datetime import datetime

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from excel_app._cls_excel_auto_manager import Process_Excel, Envio_Pdc_Wpp, EnvioErrorPdc
from conexiones_db._cls_sqlalchemy import MySQLConnector

sql_file_path = os.path.join(project_root, 'sql', '_sql_max_actualizacion_prolog.sql')

parametro_num_day = 1    

def main():
    
    # -- Config Servidor --
    schema = 'bbdd_cos_bog_chubb'

    # -- Config Excel --
    archivo_excel = r'Z:\WORKFORCE\03. Mission\Emerson Aguilar\14. Chubb\pdc_chubb_dts.xlsx'
    ruta_img = os.path.join(project_root, 'data', 'img', 'pdc')
    ruta_txt = os.path.join(project_root, 'data', 'txt', 'pdc')

    # -- Config Envio PDC --
    grupo_1 = 'INFORMES Y REPORTES CHUBB'
#    grupo_2 = ''
#    grupo_3 = ''

    # -- Config Imagenes y Grupos --
    var_captura_img = [
        
        {
            'hojas_captura_img': 'Ausentismo', 
            'rangos_captura_img': 'A1:P53', 
            'nombre_grupo': grupo_1
         },
        
#        {
#            'hojas_captura_img': 'VentasXSponsor', 
#            'rangos_captura_img': 'A1:I27', 
#            'nombre_grupo': grupo_1
#         }
         ]

    # -- Inicializador de clases -- 
    processor_excel = Process_Excel(
        schema=schema,
        archivo_excel=archivo_excel,
        var_captura_img=var_captura_img,
        ruta_img=ruta_img,
        ruta_txt=ruta_txt
    )

    # -- Ejecucion de funciones -- 
    processor_envio_wpp = Envio_Pdc_Wpp(processor_excel)
    
     #-- Ejecucion de funciones -- 
    try:
        processor_excel.delete_archivos_ruta()
        processor_excel.refresh_archivo_excel()
        processor_excel.exportar_imagenes_excel()
        processor_excel.copiar_celdas_txt()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")
    
    try:
        processor_envio_wpp.env_pdc_bot()
    except Exception as e:
        print(f"❌ Error en el proceso de envio wpp: {str(e)}")

# -- Funcion Lectura de Marcaciones -- 
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

# -- Funcion de envio mensaje de error --     
def env_error():
    
    tabla_alerta = 'bbdd_config.tb_soul_proglog'
    
    engine = MySQLConnector().get_connection(database='bbdd_config')
    print("Consultando maxima hora de actualizacion")

    query_max = leer_query(sql_file_path)
    print(f"Consulta leída, ejecutando...")

    df = pd.read_sql(query_max, engine)
    df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce')
    df['hora_ultima_llamada'] = df['hora_ultima_llamada'].fillna(pd.to_datetime('00:00:00'))

    hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
    print(f"Hora última llamada: {hora_ultima_llamada}")

    hora_actual = datetime.now().strftime('%H:%M')
    print(f"Hora actual: {hora_actual}")

    hora_ultima = datetime.strptime(hora_ultima_llamada, '%H:%M')
    hora_actual_obj = datetime.strptime(hora_actual, '%H:%M')

    diferencia_minutos = (hora_actual_obj - hora_ultima).total_seconds() / 60
    print(f"Diferencia en minutos: {diferencia_minutos:.2f}")

    processor_env_error = EnvioErrorPdc(
        tabla_alerta=tabla_alerta,
        diferencia_minutos=diferencia_minutos
        )
    
    try:
        processor_env_error.bot_envio_error()
    except Exception as e:
        print(f"❌ Error en el proceso de envio wpp: {str(e)}")

# -- If final que indica que enviar si no actualiza la tabla de marcaciones -- 
if __name__ == '__main__':

    engine = MySQLConnector().get_connection(database='bbdd_config')
    print("Consultando maxima hora de actualizacion")

    query_max = leer_query(sql_file_path)
    print(f"Consulta leída, ejecutando...")
    
    intentos = 0
    intentos_max =  7 
    intervalo_max = 120
    intervalo_consulta = 140
    processor_excel = None

    while intentos < intentos_max:
        print(f"Intento {intentos + 1} de {intentos_max}")
        try:
            df = pd.read_sql(query_max, engine)
            df['hora_ultima_llamada'] = pd.to_datetime(df['hora_ultima_llamada'], errors='coerce')
            df['hora_ultima_llamada'] = df['hora_ultima_llamada'].fillna(pd.to_datetime('00:00:00'))

            hora_ultima_llamada = df['hora_ultima_llamada'].iloc[0].strftime('%H:%M')
            print(f"Hora última llamada: {hora_ultima_llamada}")

            hora_actual = datetime.now().strftime('%H:%M')
            print(f"Hora actual: {hora_actual}")

            hora_ultima = datetime.strptime(hora_ultima_llamada, '%H:%M')
            hora_actual_obj = datetime.strptime(hora_actual, '%H:%M')

            diferencia_minutos = (hora_actual_obj - hora_ultima).total_seconds() / 60
            print(f"Diferencia en minutos: {diferencia_minutos:.2f}")

            if diferencia_minutos < intervalo_max:
                print(f"Diferencia menor a {intervalo_max} minutos, ejecutando MAIN proceso PDC")
                main()
                break
            else:
                print(f"Diferencia mayor o igual a {intervalo_max} minutos, esperando {intervalo_consulta/60} minutos e intentando nuevamente...")
                intentos += 1
                time.sleep(intervalo_consulta)
        except Exception as e:
            print(f"Error al realizar consulta debido a: {e}")
            intentos += 1
            time.sleep(intervalo_consulta)

    if intentos == intentos_max:
        print("Maximos intentos realizados, enviando mensaje de error")