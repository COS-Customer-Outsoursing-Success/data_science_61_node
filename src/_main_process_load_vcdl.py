"""""
Created By Emerson Aguilar Cruz
"""""

import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from vicidial._cls_load_vcdl import LoadListVcdl
    
def main():
    
    # -- Config Vcdl --
    user_vcdl = '1031120694'
    pass_vcdl = 'wfm1031120694'
    server_vcdl = '172.70.7.41'
    activo = 'Y'
    opcion_copiado = 'APPEND'
    indicativo_pais = '57 - COL'

    # -- Config Excel --
    ruta_cargue_vicidial = os.path.join(project_root, 'data', 'upload_vicidial')
    
    # -- Inicializador de clases -- 
    processor_load_vcdl = LoadListVcdl(

        user_vcdl=user_vcdl,
        pass_vcdl=pass_vcdl,
        server_vcdl=server_vcdl,
        activo=activo,
        opcion_copiado=opcion_copiado,
        ruta_cargue_vicidial=ruta_cargue_vicidial,
        indicativo_pais=indicativo_pais

    )

    try:
        processor_load_vcdl.cargar_vicidial()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()