import os
import subprocess

class RunScripts:

    def __init__(self, ruta_dir_scripts=None, scripts=None):
            
        self.ruta_dir_scripts = ruta_dir_scripts 
        self.scripts = scripts or []

    def run_scripts(self):
        for script in self.scripts:
            script_path = os.path.join(self.ruta_dir_scripts, script)
            if os.path.exists(script_path):
                print(f"▶️ Ejecutando Script: {script}")
                try:
                    subprocess.run(["python", script_path], check=True)
                    print(f"✅ Finalizó la ejecución de {script}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error al ejecutar {script}: {e}")
                except Exception as e:
                    print(f"⚠️ Excepción inesperada en {script}: {e}")
            else:
                print(f"⚠️ El script {script} no existe en la ruta especificada.")
