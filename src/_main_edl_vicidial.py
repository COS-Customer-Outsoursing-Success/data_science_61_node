"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)
from datetime import datetime
from vicidial._cls_edl import EdlVicidial

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    
    # -- Config Vcdl --
    user_vcdl = '1031120694'
    pass_vcdl = 'wfm1031120694'
    server_vcdl = '172.70.7.41'
    campaigns = ['TERPEL', 'FUNDACI']
    folder_xlsx = os.path.join(project_root, 'data', 'xlsx')
    os.makedirs(folder_xlsx, exist_ok=True)
    archivo_edl = os.path.join(folder_xlsx, f'edl_prueba_{timestamp}.xlsx')

    # -- Config Excel --
    
    # -- Inicializador de clases -- 
    processor = EdlVicidial(

        user_vcdl=user_vcdl,
        pass_vcdl=pass_vcdl,
        server_vcdl=server_vcdl,
        campaigns=campaigns,
        archivo_edl=archivo_edl
    )

    try:
        processor.cargar_vcdl()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()