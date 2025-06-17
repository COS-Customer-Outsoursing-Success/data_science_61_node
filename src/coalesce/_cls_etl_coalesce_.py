import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from conexiones_db._cls_sqlalchemy import MySQLConnector
from load_data._cls_load_data import *

class EtlCoalesceTelChubb:

        def __init__(self, phone_columns=None, schema=None, table=None, cuenta=None, sql_file_path=None):
            self.current_folder = os.path.dirname(os.path.abspath(__file__))
            self.project_root = os.path.dirname(os.path.dirname(self.current_folder))
            self.path_home = str(Path.home())  # "C:\Users\tu_usuario"
            self.periodo_actual = datetime.now().strftime('%Y%m')
            self.phone_columns = phone_columns
            self.schema = schema
            self.table = table
            self.engine = MySQLConnector().get_connection(database=self.schema)
            self.cuenta = cuenta
            self.sql_file_path = sql_file_path
            self.df = None
            self.loader = MySQLLoader(self.engine,self.schema,self.table)

        def coalesce_etl(self):
            print("Ejecutando proceso de repoblación telefónica...")

            try:
                with open(self.sql_file_path, 'r', encoding='utf-8') as file:
                    query_coalesce = file.read()
                print("Consulta cargada correctamente desde el archivo.")
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo en {self.sql_file_path}")
                raise
            except Exception as e:
                print(f"Error al leer el archivo SQL: {str(e)}")
                raise

            try:
                self.df = pd.read_sql(query_coalesce, self.engine)

                # Copia de las columnas telefónicas para agregar luego
                phone_cols = self.phone_columns.copy()
                df_original = self.df.copy()

                # Despivotar columnas de teléfono
                df_melted = self.df.melt(
                    id_vars=[col for col in self.df.columns if col not in self.phone_columns],
                    value_vars=self.phone_columns,
                    var_name='tipo_phone',
                    value_name='phone'
                )

                # Limpiar los números de teléfono
                df_melted['phone'] = (
                    df_melted['phone']
                    .astype(str)
                    .str.replace(r'\.0$', '', regex=True)
                    .str.replace(r'\D', '', regex=True)
                )

                # Filtrar solo teléfonos de 10 dígitos
                df_melted = df_melted[df_melted['phone'].str.len() == 10]

                # Eliminar duplicados
                df_melted = df_melted.drop_duplicates(subset=[self.cuenta, 'phone'])

                # Agregar fecha de carga
                df_melted['upload_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Traer de vuelta las columnas telefónicas originales
                # Usamos join con las columnas telefónicas y el id principal
                df_final = df_melted.merge(
                    df_original[[self.cuenta] + phone_cols],
                    on=self.cuenta,
                    how='left'
                )

                # Limpiar valores nulos
                df_final = df_final.where(pd.notnull(df_final), None)
                df_final = df_final.replace({np.nan: None})

                self.df = df_final
                print("Proceso de repoblación finalizado correctamente. DataFrame resultante:")
                print(self.df)

            except Exception as e:
                print(f"Error en el proceso de repoblación: {e}")
                raise

        def load_data(self):
            self.loader.upsert_into_table(self.df)
            return print('Load document completed')


class EtlCoalesceTel:

    def __init__(self, phone_columns=None, schema=None, table=None, cuenta=None, sql_file_path=None):
        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(self.current_folder))
        self.path_home = str(Path.home())  # "C:\Users\tu_usuario"
        self.periodo_actual = datetime.now().strftime('%Y%m')
        self.phone_columns = phone_columns
        self.schema = schema
        self.table = table
        self.engine = MySQLConnector().get_connection(database=self.schema)
        self.cuenta = cuenta
        self.sql_file_path = sql_file_path
        self.df = None
        self.loader = MySQLLoader(self.engine,self.schema,self.table)
    
    def coalesce_etl(self):
        print("Ejecutando proceso de repoblación telefónica")
        try:
            with open(self.sql_file_path, 'r', encoding='utf-8') as file:
                query_coalesce = file.read()            
            print("Consulta cargada correctamente desde el archivo.")

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo en {self.sql_file_path}")
            raise
        except Exception as e:
            print(f"Error al leer el archivo SQL: {str(e)}")
            raise
        
        try:
            self.df = pd.read_sql(query_coalesce, self.engine)

            df_melted = self.df.melt(
                id_vars=[col for col in self.df.columns if col not in self.phone_columns],
                value_vars=self.phone_columns,
                var_name='tipo_phone',
                value_name='phone'
            )
            
            df_melted['phone'] = (
                df_melted['phone']
                .astype(str)
                .str.replace(r'\.0$', '', regex=True)  
                .str.replace(r'\D', '', regex=True)    
            )
            
            df_melted = df_melted[df_melted['phone'].str.len() == 10]  
            df_melted = df_melted.drop_duplicates(subset=[self.cuenta, 'phone'])
            
            df_melted['upload_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df_melted = df_melted.where(pd.notnull(df_melted), None)
            df_melted = df_melted.replace({np.nan: None})
            self.df = df_melted
            print(self.df)
        except Exception as e:
            print(f"Error en el proceso de repoblación: {e}")
            raise

    def load_data(self):
        self.loader.upsert_into_table(self.df)
        return print('Load document completed')
