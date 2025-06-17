import os, pandas as pd, shutil, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_chrome_driver():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=os.path.join(config, 'chromedriver.exe'))
    return webdriver.Chrome(service=service, options=options)

# Función para subir archivos a BD Soul
def upload_bd_rpa():
    driver = create_chrome_driver()
    wait = WebDriverWait(driver, 40)
    driver.get("https://crmchubb.rpagroupcos.com/login")
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtusuario"]'))).send_keys(user)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtpassword"]'))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inicio_sesion"]'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="side-menu"]/li[2]/ul/li[4]/a'))).click()

    for sponsor_name, ruta in rutas.items():
        if not os.path.exists(ruta):
            print(f"El archivo {ruta} no existe. Saltando sponsor: {sponsor_name}")
            continue
        print(f"Subiendo archivo para el sponsor: {sponsor_name}")
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtSponsor"]'))).send_keys(sponsor_name)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ArchivoAdjunto"]'))).send_keys(ruta)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SubirData"]'))).click()
        time.sleep(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div[6]/button[1]'))).click()

        print(f"Archivo {sponsor_name} subido correctamente a BD RPA")
    
    driver.quit()
    print("Todos los archivos han sido subidos correctamente a BD RPA.")

def main():
    upload_bd_rpa()
    
if __name__ == "__main__":

# Variables
    config = r'C:\Users\andres.ortiz\Documents\01. Github\claro_ventas_chile\config'
    user = 'andres.ortiz'
    password = "Aa1000954083*" 
    rutas = {"Coomeva": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Coomeva.xlsx",
                "BAN100": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue BAN100.xlsx",
                "Banco W": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Banco W.xlsx",
                "ESB-Ventas": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue ESB-Ventas.xlsx",
                "Colsubsidio": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Colsubsidio.xlsx",
                "Falabella": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Falabella.xlsx",
                "MOVISTAR": r"C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Movistar.xlsx",
               }

    sponsor = [rutas.keys()]

# ejecutar
    main()