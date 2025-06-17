import os, pandas as pd, shutil, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Función auxiliar para crear driver Chrome
def create_chrome_driver():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=os.path.join(config, 'chromedriver.exe'))
    return webdriver.Chrome(service=service, options=options)

# Función para subir archivos a BD Soul
def upload_bd_soul():
    driver = create_chrome_driver()
    wait = WebDriverWait(driver, 40)

    driver.get("https://mysoul.groupcos.com/login")
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mat-input-0"]'))).send_keys(user)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mat-input-1"]'))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-login/div/div/div[2]/div/div[2]/div/div[3]/form/div[2]/button'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-mios/app-side-bar/div/mat-sidenav-container/mat-sidenav/div/mat-nav-list/a[3]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-menu-panel-1"]/div/button[2]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-menu-panel-3"]/div/div[6]/button'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-mios/app-side-bar/div/mat-sidenav-container/mat-sidenav/div/app-left-nav/div/div/div/mat-nav-list/div/a[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-mios/app-side-bar/div/mat-sidenav-container/mat-sidenav-content/div/app-forms-list/div/div/div[3]/mat-card[3]/button'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-menu-panel-8"]/div/button[3]'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))).send_keys(data)

    # Campos personalizados
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[1]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-4"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[2]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-21"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[3]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-38"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-9"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-55"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[5]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-72"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-select-value-13"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-89"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[7]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-539"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[8]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-972"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[9]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-989"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[10]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-1006"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[11]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-1023"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[12]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-191"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[13]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-208"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[14]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-225"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[15]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-242"]/span'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[1]/div[2]/div[16]/div/div[2]/mat-form-field/div/div[1]/div'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-option-259"]/span'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-0"]/div/div[2]/button/span[1]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-radio-2"]/label'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-1"]/div/div[2]/button[2]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-radio-7"]/label'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cdk-step-content-0-2"]/div/div[2]/button[2]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[3]/button[3]'))).click()
    time.sleep(40)
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[3]/button[1]'))).click()
    print("Archivo subido correctamente a BD Soul")

    driver.quit()

def main():
    upload_bd_soul()
  
if __name__ == "__main__":

# Variables
    config = r'C:\Users\andres.ortiz\Documents\01. Github\claro_ventas_chile\config'
    user = 'aortiz40'
    password = "Colombia2030*" 
    data = r'C:\Users\andres.ortiz\Documents\01. Github\Chubb\data\upload_soul_rpa\Plantilla Precargue Emcali.xlsx'

# ejecutar
    main()