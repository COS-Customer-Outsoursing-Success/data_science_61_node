import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_folder)
sys.path.append(current_folder)

from run_subprocess._cls_run_subprocess import RunScripts


def main():
    
    ruta_dir_scripts = os.path.join(project_root, 'src')

    scripts = [
                '_main_process_coalesce_chubb_ban100.py',
                '_main_process_coalesce_chubb_banco_w.py',
                '_main_process_coalesce_chubb_colsubsidio.py',
                '_main_process_coalesce_chubb_coomeva.py',
                '_main_process_coalesce_chubb_esb.py',
                '_main_process_coalesce_chubb_falabella.py',
                '_main_process_coalesce_chubb_movistar.py',

            ]

    
    # -- Inicializador de clases -- 
    processor = RunScripts(

        ruta_dir_scripts=ruta_dir_scripts,
        scripts=scripts
    )

    try:
        processor.run_scripts()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':

    main()

