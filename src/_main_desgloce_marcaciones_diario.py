"""
CREATED BY EMERSON AGUILAR CRUZ
"""

from datetime import datetime
from sql_stored_procedure._cls_ejecucion_sp import EjecucionStoredProcedure

año_actual = datetime.now().year
mes_actual = datetime.now().month
#{'nombre': 'sp_desgloce_management_dts'}, # SP SIN PARAMETROS
#{'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day}}, # SP CON PARAMETROS DE DIAS INT,

def main ():

    schema = 'bbdd_cos_bog_chubb'

    parametro_num_day = 1
    
    param_1 = 'valor1'
    
    param_2 = 'valor2'

    stored_procedures = [
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'ban100'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'banco_w'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'colsubsidio'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'coomeva'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'emcali'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'esb'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'falabella'}}, # SP CON DOS PARAMETROS
        {'nombre': 'sp_01_marcaciones_desgloce_dts_general', 'parametros': {'param1': parametro_num_day, 'param2': 'movistar'}}, # SP CON DOS PARAMETROS

    ]

    executor = EjecucionStoredProcedure(
        schema=schema,
        stored_procedures=stored_procedures)
    try:
        executor.ejecutar_sps()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")
            
if __name__ == '__main__':
    main()