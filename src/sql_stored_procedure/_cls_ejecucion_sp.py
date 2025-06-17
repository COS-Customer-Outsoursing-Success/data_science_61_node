import threading
import time
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from conexiones_db._cls_sqlalchemy import MySQLConnector

class EjecucionStoredProcedure:

    def __init__(self, schema, stored_procedures=None):
        self.schema = schema
        self.stored_procedures = stored_procedures or []
        self.parar_sp = threading.Event()

    def _cargar_indicador(self):
        while not self.parar_sp.is_set():
            for symbol in "|/-\\":
                print(f"\rEjecutando SP... {symbol}", end="", flush=True)
                time.sleep(0.1)
                if self.parar_sp.is_set():
                    break

    def ejecutar_sps(self):
        try:
            print("Conectando a MySQL usando SQLAlchemy...")
            engine = MySQLConnector.get_connection(database=self.schema)

            with engine.connect() as conexion:
                print("Conexión exitosa.")

                for sp in self.stored_procedures:
                    nombre = sp['nombre']
                    parametros = sp.get('parametros', {})

                    print(f"\nEjecutando Stored Procedure: {nombre}")
                    self.parar_sp.clear()
                    hilo_carga = threading.Thread(target=self._cargar_indicador)
                    hilo_carga.start()

                    try:
                        if parametros:
                            placeholders = ', '.join(f":{k}" for k in parametros)
                            sql = text(f"CALL {nombre}({placeholders})")
                            conexion.execute(sql, parametros)
                        else:
                            conexion.execute(text(f"CALL {nombre}()"))

                        print(f"\nSP '{nombre}' ejecutado correctamente.")
                    except Exception as e:
                        print(f"Error al ejecutar '{nombre}': {e}")
                    finally:
                        self.parar_sp.set()
                        hilo_carga.join()
                        time.sleep(1)

                print("Todos los Stored Procedures se ejecutaron.")

        except SQLAlchemyError as e:
            print(f"Error general al ejecutar SPs: {e}")
        finally:
            if 'engine' in locals():
                engine.dispose()
                print("Conexión cerrada.")
