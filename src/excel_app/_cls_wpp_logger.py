"""
Created By David Salcedo
Captura todo el stdout/stderr de una corrida a un archivo diario en
logs/, ademas de seguir mostrandolo en consola. Retiene 7 dias.
"""

import sys
import os
import glob
import time
from datetime import datetime

_current_folder = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_folder))
LOGS_DIR = os.path.join(_project_root, 'logs')

RETENCION_DIAS = 7


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


def _limpiar_logs_viejos(prefijo):
    limite = time.time() - RETENCION_DIAS * 86400
    for archivo in glob.glob(os.path.join(LOGS_DIR, f"{prefijo}_*.log")):
        try:
            if os.path.getmtime(archivo) < limite:
                os.remove(archivo)
        except OSError:
            pass


def activar_log_persistente(nombre_campana):
    """Redirige stdout/stderr para que, ademas de la consola, todo quede
    guardado en logs/{nombre_campana}_YYYY-MM-DD.log (retencion 7 dias)."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    _limpiar_logs_viejos(nombre_campana)

    fecha = datetime.now().strftime('%Y-%m-%d')
    ruta_log = os.path.join(LOGS_DIR, f"{nombre_campana}_{fecha}.log")
    archivo_log = open(ruta_log, 'a', encoding='utf-8', buffering=1)

    sys.stdout = _Tee(sys.__stdout__, archivo_log)
    sys.stderr = _Tee(sys.__stderr__, archivo_log)

    print(f"\n{'=' * 70}\n[{datetime.now().isoformat()}] Inicio de corrida\n{'=' * 70}")
