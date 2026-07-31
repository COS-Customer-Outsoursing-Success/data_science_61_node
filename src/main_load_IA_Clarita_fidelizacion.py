"""
main_load_IA_Claria_fidelizacion.py
-------------------------------------
Carga incremental del consolidado de cargue IA de fidelización al servidor .61.
Destino: bbdd_cos_bog_claro_fidelizacion.tb_ia_clarita_fidelizacion_ds

Estrategia:
  - Llave única: fecha_envio + cuenta + servicio
  - Consulta las combinaciones ya existentes en la tabla.
  - Filtra el Excel conservando solo registros nuevos (no duplicados).
  - Inserta en chunks con pandas.to_sql (bulk insert, sin truncar).
  - Mueve cada archivo procesado de Nuevo/ → Cargado/.
"""

import os
import sys
import glob
import shutil

import pandas as pd
from sqlalchemy import text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, ROOT_DIR)

from src.conexiones_db._cls_sqlalchemy import MySQLConnector

# ── Configuración ────────────────────────────────────────────────────────────
DATABASE    = "bbdd_cos_bog_claro_fidelizacion"
SCHEMA      = "bbdd_cos_bog_claro_fidelizacion"
TABLE       = "tb_ia_clarita_fidelizacion_ds"
DIR_NUEVO   = os.path.join(ROOT_DIR, "data", "Bases_IA", "Nuevo")
DIR_CARGADO = os.path.join(ROOT_DIR, "data", "Bases_IA", "Cargado")
CHUNK_SIZE  = 5_000
LLAVE       = ["fecha_envio", "cuenta", "servicio"]    # llave única del consolidado
SHEET_NAME  = "IA"                                    # pestaña del Excel a cargar


def leer_archivos(directorio: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Lee todos los .xlsx del directorio.
    Retorna (DataFrame consolidado, lista de rutas leídas).
    """
    archivos = glob.glob(os.path.join(directorio, "*.xlsx"))
    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos .xlsx en: {directorio}")

    dfs = []
    for ruta in archivos:
        print(f"  Leyendo: {os.path.basename(ruta)}")
        dfs.append(pd.read_excel(ruta, sheet_name=SHEET_NAME))

    df = pd.concat(dfs, ignore_index=True)
    print(f"  Total registros leídos: {len(df):,}")
    return df, archivos


def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas a minúscula, fecha_envio a date y elimina filas vacías."""
    df.columns = df.columns.str.lower()
    if "fecha_envio" in df.columns:
        df["fecha_envio"] = pd.to_datetime(df["fecha_envio"], errors="coerce").dt.date
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def obtener_llaves_existentes(engine) -> set:
    """
    Consulta la tabla y retorna un set de tuplas (fecha_envio, cuenta, servicio)
    que ya están cargadas — llave compuesta para control de duplicados.
    Todo se normaliza a str para evitar mismatch de tipos con el driver MySQL.
    """
    query = f"""
        SELECT DISTINCT
            DATE_FORMAT(fecha_envio, '%Y-%m-%d') AS fecha_envio,
            CAST(cuenta AS CHAR),
            TRIM(servicio)
        FROM `{SCHEMA}`.`{TABLE}`
    """
    with engine.connect() as conn:
        resultado = conn.execute(text(query))
        llaves = {(row[0], row[1], row[2]) for row in resultado}
    print(f"       Muestra de llaves en BD: {list(llaves)[:3]}")
    return llaves


def filtrar_nuevos(df: pd.DataFrame, llaves_existentes: set) -> pd.DataFrame:
    """
    Retorna solo los registros cuya combinación fecha_envio+cuenta+servicio
    no existe aún en la tabla.
    Normaliza todos los campos a str para comparación consistente con el set.
    """
    llave_df = [
        (str(f), str(int(c)) if pd.notna(c) else "", str(s).strip())
        for f, c, s in zip(df["fecha_envio"], df["cuenta"], df["servicio"])
    ]
    print(f"  Muestra de llaves en Excel: {llave_df[:3]}")
    mask = [llave not in llaves_existentes for llave in llave_df]
    df_filtrado = df[mask].reset_index(drop=True)

    # Eliminar duplicados dentro del propio Excel antes de insertar
    antes = len(df_filtrado)
    df_filtrado = df_filtrado.drop_duplicates(subset=LLAVE).reset_index(drop=True)
    if len(df_filtrado) < antes:
        print(f"  Duplicados internos del Excel eliminados: {antes - len(df_filtrado):,}")

    return df_filtrado


def mover_a_cargado(archivos: list[str], directorio_destino: str) -> None:
    """Mueve cada archivo procesado de Nuevo/ → Cargado/."""
    os.makedirs(directorio_destino, exist_ok=True)
    for ruta in archivos:
        nombre = os.path.basename(ruta)
        destino = os.path.join(directorio_destino, nombre)
        shutil.move(ruta, destino)
        print(f"  Movido: {nombre} → Cargado/")


def main():
    print("=" * 60)
    print("  CARGUE INCREMENTAL IA CLARITA FIDELIZACIÓN → .61")
    print("=" * 60)

    # 1. Leer Excel(s)
    print("\n[1/5] Leyendo archivos Excel...")
    df, archivos_leidos = leer_archivos(DIR_NUEVO)
    df = limpiar_dataframe(df)

    # 2. Conexión
    print("\n[2/5] Conectando a la base de datos...")
    engine = MySQLConnector.get_connection(database=DATABASE)
    print(f"       Conexión establecida → {DATABASE}")

    # 3. Obtener llaves ya cargadas
    print(f"\n[3/5] Verificando registros existentes en {TABLE}...")
    llaves_existentes = obtener_llaves_existentes(engine)
    print(f"       Combinaciones (fecha+cuenta+servicio) ya en tabla: {len(llaves_existentes):,}")

    # 4. Filtrar duplicados y cargar
    df_nuevo = filtrar_nuevos(df, llaves_existentes)

    if df_nuevo.empty:
        print("\n  No hay registros nuevos. La tabla ya está actualizada.")
    else:
        print(f"\n[4/5] Insertando {len(df_nuevo):,} registros nuevos en chunks de {CHUNK_SIZE:,}...")
        df_nuevo.to_sql(
            name=TABLE,
            con=engine,
            schema=SCHEMA,
            if_exists="append",
            index=False,
            chunksize=CHUNK_SIZE,
            method="multi",
        )
        print(f"       Insertados correctamente en {SCHEMA}.{TABLE}")

    engine.dispose()

    # 5. Mover archivos a Cargado/
    print(f"\n[5/5] Moviendo archivos procesados a Cargado/...")
    mover_a_cargado(archivos_leidos, DIR_CARGADO)

    print("\n✓ Proceso finalizado exitosamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()
