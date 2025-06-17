import os
import shutil
import pandas as pd
import modin.pandas as mpd
import zipfile
import gzip
import re
import tempfile
import io
from datetime import datetime

class FileReader:
    def __init__(self, use_modin=False, start_path=None, end_path=None):
        self.use_modin = use_modin
        self.start_path = start_path
        self.end_path = end_path

        if self.start_path is None:
            raise ValueError("Debe proporcionar una ruta de inicio válida.")
        if not os.path.exists(self.start_path):
            raise ValueError(f"La ruta de inicio '{self.start_path}' no existe.")
        
        # Crear la carpeta de destino si no existe y se proporciona
        if self.end_path and not os.path.exists(self.end_path):
            os.makedirs(self.end_path)

    def get_latest_file(self):
        files = [f for f in os.listdir(self.start_path) if os.path.isfile(os.path.join(self.start_path, f))]
        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(self.start_path, f)))
        return os.path.join(self.start_path, latest_file)

    def read_file(self, file_path, **kwargs):
        file_extension = os.path.splitext(file_path)[1].lower()
        print(f"Leyendo archivo: {file_path}")
        
        # Obtener la fecha de creación
        creation_time = self.get_creation_time(file_path)
        creation_date = datetime.strptime(creation_time, '%Y-%m-%d %H:%M:%S')
        year_month = creation_date.strftime('%Y%m')

        # Imprimir la fecha de creación
        print(f"Fecha y hora de creación: {creation_time}")

        # Leer el archivo según su extensión
        if file_extension == '.csv':
            df = self._read_csv(file_path, **kwargs)
        elif file_extension in ['.xlsx', '.xls']:
            df = self._read_excel(file_path, **kwargs)
        elif file_extension == '.txt':
            df = self._read_txt(file_path, **kwargs)
        elif file_extension == '.zip':
            df = self._read_zip(file_path, **kwargs)
        elif file_extension == '.gz':
            df = self._read_gz(file_path, **kwargs)
        else:
            raise ValueError(f"Formato de archivo {file_extension} no soportado.")

        # Agregar las columnas de fecha y año-mes al DataFrame
        df['fecha_asignacion'] = creation_time
        df['periodo'] = int(year_month)

        # Limpiar los datos (eliminar tildes, punto y coma, y comas)
        df = self._clean_data(df)

        return df

    def _read_csv(self, file_path, **kwargs):
        print("Leyendo archivo CSV con manejo avanzado")
        with open(file_path, 'r', encoding=kwargs.get('encoding', 'utf-8'), errors='replace') as file:
            content = file.read()
        
        # Usar StringIO para manejar el contenido como flujo de texto
        string_io = io.StringIO(content)
        
        if self.use_modin:
            print("Usando Modin para leer CSV")
            df = mpd.read_csv(string_io, **kwargs)  # Evitar usar la primera columna como índice
        else:
            print("Usando Pandas para leer CSV")
            df = pd.read_csv(string_io, **kwargs)  # Evitar usar la primera columna como índice

        return self._clean_headers(df)

    def _read_excel(self, file_path, **kwargs):
        if self.use_modin:
            print("Usando Modin para leer Excel")
            df = mpd.read_excel(file_path, **kwargs)
        else:
            print("Usando Pandas para leer Excel")
            df = pd.read_excel(file_path, **kwargs)

        return self._clean_headers(df)

    def _read_txt(self, file_path, **kwargs):
        print("Leyendo archivo TXT con manejo avanzado")
        with open(file_path, 'r', encoding=kwargs.get('encoding', 'utf-8'), errors='replace') as file:
            content = file.read()
        
        # Usar StringIO para manejar el contenido como flujo de texto
        string_io = io.StringIO(content)
        
        df = pd.read_csv(string_io, **kwargs)  # Evitar usar la primera columna como índice
        return self._clean_headers(df)

    def _read_zip(self, file_path, **kwargs):
        print("Leyendo archivo ZIP con manejo avanzado")
        dataframes = []
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                file_name = file_info.filename
                # Saltar directorios
                if file_info.is_dir():
                    continue

                # Obtener la extensión del archivo dentro del ZIP
                extension = os.path.splitext(file_name)[1].lower()

                # Leer el archivo dentro del ZIP en memoria
                with zip_ref.open(file_info) as f:
                    content = f.read()
                    # Decodificar el contenido según el encoding especificado o utf-8 por defecto
                    encoding = kwargs.get('encoding', 'utf-8')
                    text = content.decode(encoding, errors='replace')
                    string_io = io.StringIO(text)

                # Leer el archivo desde StringIO
                if extension == '.csv':
                    if self.use_modin:
                        print(f"Usando Modin para leer {file_name}")
                        df = mpd.read_csv(string_io, **kwargs)
                    else:
                        print(f"Usando Pandas para leer {file_name}")
                        df = pd.read_csv(string_io, **kwargs)
                elif extension in ['.xlsx', '.xls']:
                    # Para archivos Excel, necesitamos escribirlos a un archivo temporal
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                    temp_file.close()
                    
                    if self.use_modin:
                        print(f"Usando Modin para leer {file_name}")
                        df = mpd.read_excel(temp_file_path, **kwargs)
                    else:
                        print(f"Usando Pandas para leer {file_name}")
                        df = pd.read_excel(temp_file_path, **kwargs)
                    
                    os.remove(temp_file_path)
                elif extension == '.txt':
                    print(f"Leyendo archivo TXT {file_name} con manejo avanzado")
                    if self.use_modin:
                        df = mpd.read_csv(string_io, **kwargs)
                    else:
                        df = pd.read_csv(string_io, **kwargs)
                else:
                    print(f"Formato {extension} dentro del ZIP no soportado.")
                    continue

                # Limpiar encabezados y agregar al listado de DataFrames
                df = self._clean_headers(df)
                dataframes.append(df)

        if dataframes:
            return pd.concat(dataframes)
        else:
            raise ValueError("No se pudieron leer archivos dentro del ZIP.")

    def _read_gz(self, file_path, **kwargs):
        print("Leyendo archivo GZ")
        with gzip.open(file_path, 'rt', encoding=kwargs.get('encoding', 'utf-8'), errors='replace') as f:
            content = f.read()
            string_io = io.StringIO(content)
        
        df = self._read_csv(string_io, **kwargs)
        return df

    def read_directory(self, **kwargs):
        try:
            latest_file_path = self.get_latest_file()
            data = self.read_file(latest_file_path, **kwargs)

            if self.end_path:
                self.move_file(os.path.basename(latest_file_path))

            return data  # Retornar el DataFrame directamente

        except ValueError as e:
            print(e)
            return None  # O lanzar una excepción o retornar un DataFrame vacío si prefieres

    def move_file(self, file_name):
        source = os.path.join(self.start_path, file_name)
        destination = os.path.join(self.end_path, file_name)

        try:
            shutil.move(source, destination)
            print(f"Archivo {file_name} movido a {self.end_path}")
        except Exception as e:
            print(f"No se pudo mover el archivo {file_name}: {e}")

    def _clean_headers(self, df):
        accents_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ñ': 'n', 'Ñ': 'n'
        }

        def clean_column(col):
            for accented_char, plain_char in accents_map.items():
                col = col.replace(accented_char, plain_char)
            col = re.sub(r'[^a-zA-Z0-9]', '_', col)
            col = col.strip().lower()
            return col

        df.columns = [clean_column(col) for col in df.columns]
        print(f"Encabezados limpiados: {df.columns}")
        return df

    def _clean_data(self, df):
        # Mapa de caracteres con tildes a sus equivalentes sin tildes
        accents_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ñ': 'n', 'Ñ': 'n'
        }

        # Función para limpiar una celda individual
        def clean_cell(value):
            if isinstance(value, str):  # Solo limpiar si es un string
                # Reemplazar tildes y caracteres especiales
                for accented_char, plain_char in accents_map.items():
                    value = value.replace(accented_char, plain_char)
                # Eliminar punto y coma y comas, pero mantener puntos
                value = value.replace(';', '')  # Eliminar punto y coma
                value = value.replace(',', '')  # Eliminar comas
                # Mantener los puntos tal como están
                value = value.strip()
            return value

        # Aplicar la limpieza a todo el DataFrame
        df = df.applymap(clean_cell)
        return df

    def get_creation_time(self, file_path):
        creation_time = os.path.getctime(file_path)
        return datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
