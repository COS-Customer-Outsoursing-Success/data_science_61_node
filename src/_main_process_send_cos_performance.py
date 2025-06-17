"""""
Created By Emerson Aguilar Cruz
"""""

import os
from datetime import datetime, timedelta
from outlook_app._cls_send_correo_outlook import EnvioCorreoOutlook
from src.excel_app._cls_excel_auto_manager import Process_Excel

def main():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_folder)
    archivo_excel = r'Z:\WORKFORCE\03. Mission\Emerson Aguilar\01.Claro\01.Claro Proactivas\03.Informes\01. Cos Performance\01.Informe_Cos_Performance_Claro_Proactivas_Fidelizacion_Buck.xlsx'
    ruta_img = os.path.join(project_root, 'data', 'img', 'outlook', 'cos_performance')
    ruta_txt = os.path.join(project_root, 'data', 'txt', 'outlook', 'cos_performance')

    var_captura_img = [

        {
            'hojas_captura_img': 'Ausentismo_Adherencia', 
            'rangos_captura_img': 'B2:V42'
         },

        {
            'hojas_captura_img': 'Ocupacion_Utilizacion', 
            'rangos_captura_img': 'B2:V42'
         },

        {
            'hojas_captura_img': 'Comportamiento_Auxiliares', 
            'rangos_captura_img': 'E2:L49'
         }
    ]

    processor_xlsx = Process_Excel(
        archivo_excel=archivo_excel,
        var_captura_img=var_captura_img,
        ruta_img=ruta_img,
        ruta_txt=ruta_txt
    )

    try:
        processor_xlsx.delete_archivos_ruta()
        processor_xlsx.kill_excel()
        processor_xlsx.refresh_archivo_excel()
        processor_xlsx.kill_excel()
        processor_xlsx.exportar_imagenes_excel()
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

    destinatarios = ["Milton.Duran@groupcosbpo.com"]  
    destinatarios_copia = ["Albeiro.Hernandez@groupcosbpo.com"]  
    asunto = "Informe COS PERFORMANCE Test"
    ayer = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")
    cuerpo_correo = f'Se realiza envió de informe COS PERFORMANCE actualizado a corte del {ayer}. Se adjunta detalle para su validación' 
    texto_adicional = 'Quedo atento a cualquier tipo de novedad que se tenga en relacion a lo enviado'
    archivo = archivo_excel    
    try:
        processor = EnvioCorreoOutlook(
            destinatarios=destinatarios,
            destinatarios_copia=destinatarios_copia,
            asunto=asunto,
            cuerpo_correo=cuerpo_correo,
            texto_adicional=texto_adicional,
            archivo=archivo
        )
        
        processor.enviar_correo()
        
        print("✅ Correo enviado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")

if __name__ == '__main__':
    main()