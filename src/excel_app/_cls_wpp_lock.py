"""
Created By David Salcedo
Candado entre procesos: evita que dos campanas usen el servicio
WhatsApp (puerto 3000) al mismo tiempo. Si el proceso dueno del
candado ya no existe (crash previo), se libera automaticamente.
"""

import os
import time
import psutil

_current_folder = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_current_folder))
LOCK_PATH = os.path.join(_project_root, 'whatsapp_service', '.wpp.lock')

TIMEOUT_SEGUNDOS = 600  # 10 minutos
POLL_SEGUNDOS = 5


def _pid_existe(pid):
    try:
        return psutil.pid_exists(pid)
    except Exception:
        return True  # ante la duda, no asumir que esta muerto


def _limpiar_lock_si_esta_huerfano():
    if not os.path.exists(LOCK_PATH):
        return
    try:
        with open(LOCK_PATH, 'r') as f:
            pid_dueno = int(f.read().strip())
        if not _pid_existe(pid_dueno):
            os.remove(LOCK_PATH)
            print(f"[WPP-LOCK] Candado huerfano del PID {pid_dueno} (proceso ya no existe). Liberado.")
    except (ValueError, FileNotFoundError):
        try:
            os.remove(LOCK_PATH)
        except FileNotFoundError:
            pass


def adquirir_lock_wpp(timeout_segundos=TIMEOUT_SEGUNDOS):
    """Bloquea hasta que el servicio WhatsApp este libre o se agote el
    tiempo de espera. Devuelve True si se obtuvo el candado, False si
    se agoto el timeout (otra campana sigue activa)."""
    inicio = time.time()
    while True:
        _limpiar_lock_si_esta_huerfano()
        try:
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except FileExistsError:
            transcurrido = time.time() - inicio
            restante = timeout_segundos - transcurrido
            if restante <= 0:
                return False
            print(f"[WPP-LOCK] Servicio ocupado por otra campaña, esperando... ({int(transcurrido)}s/{timeout_segundos}s)")
            time.sleep(min(POLL_SEGUNDOS, restante))


def liberar_lock_wpp():
    try:
        os.remove(LOCK_PATH)
    except FileNotFoundError:
        pass
