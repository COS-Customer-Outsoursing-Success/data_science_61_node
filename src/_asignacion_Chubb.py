import pandas as pd
import os
from _cls_sqlalchemy import MySQLConnector61 as ms
from _cls_load_data import LoadDataframePandas as ld
from datetime import datetime as dt
import re


class Download_Assignment:

    def __init__(self, varSchema, varTable, mes_siguiente=False, filtro_base=None):
        self.varSchema = varSchema
        self.engine = ms.funConectMySql(self.varSchema)
        self.varTable = varTable
        self.today = dt.now()
        self.filtro_base = filtro_base

        if mes_siguiente:
            self.custom_date = dt(self.today.year + 1, 1, 1) if self.today.month == 12 else dt(self.today.year, self.today.month + 1, 1)
        else:
            self.custom_date = self.today

    def convert_excel_date(self, series):
        return pd.to_datetime(
            pd.to_numeric(series, errors='coerce'),
            origin='1899-12-30',
            unit='d',
            errors='coerce'
        ).fillna(
            pd.to_datetime(series, errors='coerce')
        )
  
    def structure(self):
        for folder in folders:
            if self.filtro_base not in folder:
                continue

            folder_path = os.path.join(parent_folder, 'data', folder)

            if 'COS_Bases_Ban100' in folder:
                self.varTable = 'tb_asignacion_ban100_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_excel(file_path)
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period

                    for col in ['FecApertura', 'FecUltimoMovimiento', 'FecExpedicionDocumento', 'FecNacimiento']:
                        self.df[col] = self.convert_excel_date(self.df[col])

                    self.Insert_MySql61()

            elif 'COS_Bases_Banco_W' in folder:
                self.varTable = 'tb_asignacion_banco_w_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_excel(file_path)
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period

                    for col in ['FecApertura', 'FecUltimoMovimiento', 'FecExpedicionDocumento', 'FecNacimiento']:
                        self.df[col] = self.convert_excel_date(self.df[col])

                    self.df.drop('VlrSaldo', axis=1, inplace=True)
                    self.Insert_MySql61()

            elif 'COS_Bases_Colsubsidio' in folder:
                self.varTable = 'tb_asignacion_colsubsidio_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if 'Novedades' in file:
                        column_mapping = {
                            'Tipo_Id': 'Tipo_id',
                            'Numero_Id': 'Documento',
                            'Nombre_completo': 'Nombre completo',
                            'Razon_Social': 'Razon_social',
                            'Fecha_Nacimiento': 'Fecha_Nacimiento',
                            'DIRECCION_RESIDENCIA_PERSONA': 'Direccion',
                            'CORREO_ELECTRONICO_1': 'Correo',
                            'TELEFONO_CELULAR_1': 'Telefono1',
                            'Tipo_Segmento': 'Segmento',
                            'AUTORIZACION': 'Autoriza',
                            'Numero_Beneficiarios': 'No_Beneficiarios',
                            'Nombres_Beneficiarios': 'nombre_beneficiario',
                        }
                        self.df = pd.read_excel(file_path)
                        self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                        self.df = self.df.rename(columns=column_mapping)
                        curdate = self.custom_date.strftime('%Y-%m-%d')
                        period = self.custom_date.strftime('%Y%m')
                        self.df['NIT'] = self.df['Id_Empresa'].astype(str).str.replace(r'^(NIT|CC)\s*', '', regex=True).str.strip()
                        self.df['Cargo'] = 'Sin informacion'
                        self.df['Estado_civil'] = 'Sin informacion'
                        self.df['Fecha_Nacimiento'] = self.convert_excel_date(self.df['Fecha_Nacimiento'])
                        self.df['Edad'] = (self.today.year - self.df['Fecha_Nacimiento'].dt.year - (
                                (self.today.month < self.df['Fecha_Nacimiento'].dt.month) |
                                ((self.today.month == self.df['Fecha_Nacimiento'].dt.month) & (self.today.day < self.df['Fecha_Nacimiento'].dt.day))
                        ))
                        self.df['Fecha_expedicion'] = 'Sin informacion'
                        self.df['Ciudad'] = 'Sin informacion'
                        self.df['Telefono2'] = 'Sin informacion'
                        self.df['Fecha_afiliacion'] = self.convert_excel_date(self.df['FechaAfiliacion'])
                        self.df['Categoria'] = 'Sin informacion'
                        self.df['Genero'] = 'Sin informacion'
                        self.df['Cuota_monetaria'] = 'Sin informacion'
                        self.df['Tipo'] = 'Novedades'
                        self.df['upload_date'] = curdate
                        self.df['period'] = period
                        self.df = self.df[[
                            "Tipo_id", "Documento", "Nombre completo", "NIT", "Razon_social", "Cargo",
                            "Estado_civil", "Fecha_Nacimiento", "Edad", "Fecha_expedicion", "Direccion",
                            "Ciudad", "Correo", "Telefono1", "Telefono2", "Fecha_afiliacion", "Categoria",
                            "Genero", "Segmento", "Autoriza", "Cuota_monetaria", "Tipo", "No_Beneficiarios",
                            'upload_date', 'period', 'nombre_beneficiario'
                        ]]
                        self.Insert_MySql61()
                    elif 'Modelo' in file:
                        column_mapping = {
                            'tipoidentificacion': 'Tipo_id',
                            'numeroidentificacion': 'Documento',
                            'nit_empresa': 'NIT',
                            'razon_social': 'Razon_social',
                            'cargo': 'Cargo',
                            'estado_civil': 'Estado_civil',
                            'fechanacimiento': 'Fecha_Nacimiento',
                            'edad': 'Edad',
                            'fecha_expedición': 'Fecha_expedicion',
                            'direccion_casa': 'Direccion',
                            'ciudad': 'Ciudad',
                            'correo_electronico': 'Correo',
                            'telefono_celular': 'Telefono1',
                            'telefono_residencia': 'Telefono2',
                            'fechaafiliacion': 'Fecha_afiliacion',
                            'categoria': 'Categoria',
                            'sexo': 'Genero',
                            'segmento_poblacional': 'Segmento',
                            'autorizacion': 'Autoriza',
                            'nocuotasmonetarias': 'Cuota_monetaria',
                            'nopersonasacargo': 'No_Beneficiarios',
                        }
                        self.df = pd.read_excel(file_path)
                        self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                        self.df = self.df.rename(columns=column_mapping)
                        curdate = self.custom_date.strftime('%Y-%m-%d')
                        period = self.custom_date.strftime('%Y%m')
                        self.df['Nombre completo'] = (self.df['primernombre'].fillna('') + ' ' + self.df['segundonombre'].fillna('') + ' ' + self.df['primerapellido'].fillna('') + ' ' + self.df['segundoapellido'].fillna('')).str.strip().replace(r'\s+', ' ', regex=True)
                        self.df['Fecha_Nacimiento'] = self.convert_excel_date(self.df['Fecha_Nacimiento'])
                        self.df['Fecha_afiliacion'] = self.convert_excel_date(self.df['Fecha_afiliacion'])
                        self.df['Tipo'] = 'Modelo'
                        self.df['upload_date'] = curdate
                        self.df['period'] = period
                        self.df = self.df[[
                            "Tipo_id", "Documento", "Nombre completo", "NIT", "Razon_social", "Cargo",
                            "Estado_civil", "Fecha_Nacimiento", "Edad", "Fecha_expedicion", "Direccion",
                            "Ciudad", "Correo", "Telefono1", "Telefono2", "Fecha_afiliacion", "Categoria",
                            "Genero", "Segmento", "Autoriza", "Cuota_monetaria", "Tipo", "No_Beneficiarios",
                            'upload_date', 'period','nombre_beneficiario'
                        ]]
                        self.Insert_MySql61()

            elif 'COS_Bases_Coomeva' in folder:
                self.varTable = 'tb_asignacion_coomeva_v2'
                dataframes = []
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    df_temp = pd.read_excel(file_path)
                    if 'nuevo' in file:
                        df_temp.rename(columns={'Nombre...39': 'Nombre...36'}, inplace=True)
                        df_temp.drop(['IPB', 'CUOTA_SOLIDARIDAD', 'NIVEL DE RIESGO'], axis=1, inplace=True)
                    dataframes.append(df_temp)
                df_final = pd.concat(dataframes, ignore_index=True)
                df_final = df_final.rename(columns=lambda x: x.strip())
                curdate = self.custom_date.strftime('%Y-%m-%d')
                period = self.custom_date.strftime('%Y%m')
                df_final['upload_date'] = curdate
                df_final['period'] = period
                self.df = df_final
                self.Insert_MySql61()

            elif 'COS_Movistar' in folder:
                self.varTable = 'tb_asignacion_movistar_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_csv(file_path)
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period
                    self.Insert_MySql61()

            elif 'COS_Bases_Falabella' in folder:
                self.varTable = 'tb_asignacion_falabella_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_excel(file_path)
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period
                    self.Insert_MySql61()

            elif 'COS_Emcali' in folder:
                self.varTable = 'tb_asignacion_Emcali_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_excel(file_path, sheet_name='Hoja1')
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    self.df = self.df[['CARGUE_A_OP', 'ID_Transaccion_Referencia', 'Parentesco', 'Diario_De_Vtas',
                                       'Fecha_de_vigencia', 'Prima', 'Folio', 'Asegurado', 'Genero',
                                       'CC_Aseguado_Ppal', 'AAAAMMDD_Nacimiento_PpalBen', 'Direccion', 'Correo',
                                       'Telefono', 'Ciudad', 'No_Suscriptor', 'Plan', 'Refenrencia', 'Barrio',
                                       'edad', 'APT', 'Mes', 'Campaña', 'Producto', 'Estrato', 'ciclo',
                                       'Direccion_riesgo_hogar', 'Beneficiario1', 'Parentezco']]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period
                    self.df['Diario_De_Vtas'] = self.convert_excel_date(self.df['Diario_De_Vtas'])
                    self.df = self.df[(self.df['ID_Transaccion_Referencia'] == 1) & (self.df['Diario_De_Vtas'].dt.strftime('%Y%m') == period)]
                    #self.df = self.df[(self.df['ID_Transaccion_Referencia'] == 1)]
                    self.Insert_MySql61()

            elif 'COS_Esb' in folder:
                self.varTable = 'tb_asignacion_Esb_v2'
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    self.df = pd.read_excel(file_path)
                    self.df.columns = [re.sub(r"^\d", "col_", re.sub(r"\s+", "_", re.sub(r"[^\w\s]", "", str(c).strip()))) for c in self.df.columns]
                    curdate = self.custom_date.strftime('%Y-%m-%d')
                    period = self.custom_date.strftime('%Y%m')
                    self.df['upload_date'] = curdate
                    self.df['period'] = period
                    self.Insert_MySql61()

    def Insert_MySql61(self):
        print("Ejecutando Insert en MySQL...")
        try:
            ld.funInsertDFNotTruncate(self.engine, self.df, self.varSchema, self.varTable)
            print(f"Se ha descargado y subido a MySQL la asignación, con una cantidad de registros de {self.df.shape[0]}")
        except Exception as e:
            print("Error al ejecutar el insert:", e)
            print("Se cierra la conexión.")

    def main(self):
        self.structure()


if __name__ == "__main__":

    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder)
    folders = os.listdir(os.path.join(parent_folder, 'data'))
    varSchema = "bbdd_cos_bog_chubb"
    varTable = None

    print("Seleccione el tipo de carga:")
    print("1. Base nueva mes siguiente")
    print("2. Base nueva mes actual")
    opcion_fecha = input("Ingrese 1 o 2: ")
    mes_siguiente = True if opcion_fecha == "1" else False

    print("\nSeleccione la base que desea procesar:")
    bases_disponibles = [folder for folder in folders if folder.startswith("COS_")]
    for idx, base in enumerate(bases_disponibles, start=1):
        print(f"{idx}. {base}")

    try:
        seleccion = int(input("Ingrese el número de la base: "))
        filtro_base = bases_disponibles[seleccion - 1]
    except (ValueError, IndexError):
        print("Selección inválida.")
        exit()

    bot = Download_Assignment(varSchema, varTable, mes_siguiente, filtro_base)
    bot.main()
