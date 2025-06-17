# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 18:37:59 2024

@author: Ronal.Barberi
"""

#%% Import libraries

import os
import pandas as pd
from datetime import datetime
from _cls_sqlalchemy import MySQLConnector61 as ms # To execute from cmd
# from src._cls_sqlalchemy import MySQLConnector61 as ms # To execute directly from python interpreter

#%% Create class

class Export_BD:
    def __init__(self, varSchema, varSqlPath):
        self.varSchema = varSchema
        self.engine = ms.funConectMySql(self.varSchema)
        self.varSqlPath = varSqlPath
    
    def ReadSQLCreateDataframe(self):
        print("Exportando bds en las rutas.")
        for sql_arch, path_export in self.varSqlPath.items():
            print(f"Exportando {path_export}.")
            with open(sql_arch, "r") as sql_file:
                exec_query = sql_file.read()
            df = pd.read_sql_query(exec_query, self.engine)

            df = df.loc[:, ~df.columns.duplicated()]

            if '_depurador_predictivo_coomeva.sql' in sql_arch:
                tarjetas = df[df['campana'].isin(['TARJETA PROTEGIDA STOCK', 'Tarjeta Protegida Nuevos'])]
                mochila = df[df['campana'] == 'MOCHILA']
                proteccion = df[df['campana'] == 'MAS PROTECCION']

                tarjetas.to_csv(os.path.join(parent_folder, 'data', 'upload_vicidial', f'COTARCH2 - {curdate}.csv'), index=False)
                mochila.to_csv(os.path.join(parent_folder, 'data', 'upload_vicidial', f'COMOCH - {curdate}.csv'), index=False)
                proteccion.to_csv(os.path.join(parent_folder, 'data', 'upload_vicidial', f'COMASCOS - {curdate}.csv'), index=False)
            else:
                if path_export.endswith('.csv'):
                    df.to_csv(path_export.format(curdate=curdate), index=False)
                elif path_export.endswith('.xlsx'):
                    df.to_excel(path_export.format(curdate=curdate), index=False)
                else:
                    raise ValueError(f"Formato de archivo no soportado para {path_export}")

    def Eliminar(self):
        carpetas = [
            os.path.join(parent_folder, 'data', 'upload_vicidial'),

            
        ]

        # Eliminar todos los archivos dentro de cada carpeta
        for carpeta in carpetas:
            for archivo in os.listdir(carpeta):
                ruta_archivo = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                    print(f'Archivo eliminado: {ruta_archivo}')
    
    def main(self):
        self.Eliminar() 
        self.ReadSQLCreateDataframe()

#%% Use class

current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder)
curdate = datetime.now()
curdate = curdate.strftime('%Y_%m_%d')

if __name__ == "__main__":
    varSchema = "bbdd_cos_bog_win"
    varSqlPath = {
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_ban100.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'CHUBBAN1 - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_bancow.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'BANCHUB2 - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_colsubsidio.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'COLSAPI2 - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_coomeva.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'COMASCOS - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_emcali.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'EMCALI - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_esb.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'TMKESB2 - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_falabella.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'FAAPCOS - {curdate}.csv'),
        os.path.join(parent_folder, 'sql', '_depurador_predictivo_movistar.sql'): os.path.join(parent_folder, 'data', 'upload_vicidial', f'MOV_CHUB - {curdate}.csv'),
        
        }
    
    bot = Export_BD(varSchema, varSqlPath)
    bot.main()
