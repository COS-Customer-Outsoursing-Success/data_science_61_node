
import os
import json
from pdc_paralelo._cls_pdc_orquestador import PdcOrquestador

def main():

    current_folder = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_folder)
    config_path = os.path.join(project_root, 'config', 'config_pdc.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config_json = json.load(f)

    campañas_config = [
        config_json["config_pdc_chubb"],
        config_json["config_pdc_colsubsidio"],
        config_json["config_pdc_colsubsidio_atraccion"]
    ]

    orquestador = PdcOrquestador(campañas_config)
    orquestador.ejecutar()


if __name__ == '__main__':
    
    main()
