"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys
current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)
from vicidial._cls_scraping_detalle_agente import DetalleAgenteVcdl

def main():
    
    current_folder = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_folder))

# --Config Servidor--
    schema = 'bbdd_cos_bog_claro_fidelizacion'
    table = 'tb_detalle_agente_daily_new'

# --Config Vcdl--
    user_vcdl = '1031120694'
    pass_vcdl = '103112069400'
    server_vcdl = 'miosapp.groupcos.com'
    campanas_vcdl = ['FIDESMS', 'FIDICS'] 
    download_path = os.path.join(project_root, 'data', 'detalle_agente')

    
    processor = DetalleAgenteVcdl(
        schema=schema,
        table=table,
        user_vcdl=user_vcdl,
        pass_vcdl=pass_vcdl,
        server_vcdl=server_vcdl,
        campanas_vcdl=campanas_vcdl,
        download_path=download_path
    )

    try:
        processor.eliminar_archivos_ruta()
        processor.descargar_reporte()
        processor.process_downloaded_file()
        processor.load_data()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")
    
if __name__ == '__main__':
    main()
