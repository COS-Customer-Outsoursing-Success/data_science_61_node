from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
import os
import shutil
from dateutil.relativedelta import relativedelta
import re

class KiteworksChubb:
    def __init__(self):
        """Inicializa la clase con configuraciones básicas, rutas y parámetros necesarios para la automatización"""
        self.inicio = datetime.datetime.now()
        self.path_chrome_driver = r"C:\Users\andres.ortiz\Documents\01. Github\claro_win\config\chromedriver.exe"
        self.direct_link = "https://securetransfer-nala.chubb.com/#/folder/7977f91a-7121-46c0-be27-4a582054c29c"
        
        today = datetime.datetime.now()
        self.start_date = (today - relativedelta(months=1)).replace(day=25)
        self.end_date = today.replace(day=5)
        
        self.target_folders = [
            "COS - Bases Coomeva", "COS - Movistar",'COS - Bases Banco W',
            'COS - Bases Falabella','COS - Bases Colsubsidio','COS - Bases Ban100',
            'COS - Serfinanza','COS - Bases Falabella Compra Protegida'
        ]
        
        self.base_download_dir = r'Z:\WORKFORCE\02. Workforce\WFM_CAMPANAS\Chubb_v2\Kiteworks'
        self.driver = None

    def setup_driver(self):
        """Configura y retorna una instancia de Chrome WebDriver con opciones personalizadas para descargas automáticas"""
        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(executable_path=self.path_chrome_driver)
        return webdriver.Chrome(service=service, options=options)

    def find_element(self, driver_or_element, selectors):
        """Busca elementos usando múltiples selectores XPath y retorna el primer elemento visible encontrado"""
        for selector in selectors:
            try:
                if isinstance(driver_or_element, webdriver.Chrome):
                    elements = driver_or_element.find_elements(By.XPATH, selector)
                else:
                    elements = driver_or_element.find_elements(By.XPATH, selector)
                    
                for element in elements:
                    if element.is_displayed():
                        return element
            except:
                continue
        return None

    def click_element(self, element):
        """Intenta hacer clic en un elemento usando el método estándar o JavaScript si falla"""
        try:
            element.click()
            return True
        except:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                print(f"Error al hacer clic: {e}")
                return False

    def login(self):
        """Maneja el proceso de inicio de sesión en Kiteworks usando credenciales predefinidas"""
        self.driver.get(self.direct_link)
        time.sleep(3)
        
        if "signin" in self.driver.current_url or len(self.driver.find_elements(By.ID, "email")) > 0:
            print("Iniciando sesión...")
            
            email_field = self.find_element(self.driver, ['//*[@id="email"]', '//input[@type="email"]'])
            if email_field:
                email_field.send_keys('ana.yannuzzi@groupcosbpo.com')
                time.sleep(0.5)
                
                continue_btn = self.find_element(self.driver, [
                    '//*[@id="signinApp"]/div[1]/div[2]/div/div[1]/div[3]/button',
                    '//button[contains(text(), "Continuar")]'
                ])
                if continue_btn:
                    self.click_element(continue_btn)
                    time.sleep(1.5)
                    
                    password_field = self.find_element(self.driver, ['//*[@id="password"]', '//input[@type="password"]'])
                    if password_field:
                        password_field.send_keys('Colombia759.*')
                        time.sleep(0.5)
                        
                        login_btn = self.find_element(self.driver, [
                            '//*[@id="signinApp"]/div[1]/div[2]/div/div[1]/div/div[4]/button',
                            '//button[contains(text(), "Iniciar")]'
                        ])
                        if login_btn:
                            self.click_element(login_btn)
                            time.sleep(10)
                            print("Sesión iniciada exitosamente")
        else:
            print("Ya existe una sesión activa")

    def parse_date(self, date_text):
        """Convierte texto de fecha en español a objeto datetime, manejando múltiples formatos y expresiones relativas"""
        try:
            if "por" in date_text:
                date_text = date_text.split("por")[0].strip()
            
            if "Hoy" in date_text:
                return datetime.datetime.now()
            elif "Ayer" in date_text:
                return datetime.datetime.now() - datetime.timedelta(days=1)
            
            month_pattern = re.search(r'(\w{3})\s+(\d{1,2})(?:,)?\s+(\d{4})', date_text)
            if month_pattern:
                month_str, day_str, year_str = month_pattern.groups()
                month_map = {
                    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
                    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
                }
                month = month_map.get(month_str.lower(), 1)
                day = int(day_str)
                year = int(re.search(r'(\d{4})', year_str).group(1))
                return datetime.datetime(year, month, day)
            
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]:
                try:
                    clean_date = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})', date_text)
                    if clean_date:
                        return datetime.datetime.strptime(clean_date.group(1), fmt)
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error parseando fecha '{date_text}': {e}")
            return None

    def find_latest_subfolder(self):
        """Encuentra y retorna la subcarpeta más reciente basándose en la fecha de modificación"""
        subfolders = []
        
        folder_rows = self.driver.find_elements(By.XPATH, "//div[@role='row' and contains(@aria-label, 'Fila')]")
        if not folder_rows:
            folder_rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'tr') and contains(@class, 'flex')]")
        
        for row in folder_rows:
            try:
                folder_icons = row.find_elements(By.XPATH, ".//div[contains(@class, 'file-list-icon')]")
                if not folder_icons:
                    continue
                    
                name_element = row.find_element(By.XPATH, ".//span[@class='break-all']")
                folder_name = name_element.text
                
                date_text = ""
                try:
                    time_element = row.find_element(By.XPATH, ".//time")
                    date_text = time_element.text.split("\n")[0]
                except:
                    try:
                        date_element = row.find_element(By.XPATH, ".//p[contains(@class, 'line-clamp-2')]")
                        date_text = date_element.text.split("\n")[0]
                    except:
                        continue
                
                file_date = self.parse_date(date_text)
                if file_date:
                    subfolders.append({
                        "element": row,
                        "name": folder_name,
                        "date": date_text,
                        "datetime": file_date
                    })
            except:
                continue
        
        if subfolders:
            subfolders.sort(key=lambda x: x["datetime"], reverse=True)
            print(f"Subcarpeta más reciente: {subfolders[0]['name']} ({subfolders[0]['date']})")
            return subfolders[0]
        
        print("No se encontraron subcarpetas")
        return None

    def download_files(self, folder_category, target_dir):
        """Descarga archivos Excel/CSV dentro del rango de fechas especificado desde la carpeta actual"""
        file_rows = self.driver.find_elements(By.XPATH, "//div[@role='row' and contains(@aria-label, 'Fila')]")
        if not file_rows:
            file_rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'tr') and contains(@class, 'flex')]")
        
        if not file_rows:
            print("No se encontraron archivos")
            return
        
        print(f"Encontrados {len(file_rows)} elementos")
        
        files_to_download = []
        for row in file_rows:
            try:
                file_name_element = self.find_element(row, [
                    ".//a[contains(@aria-label, 'Ir al archivo')]",
                    ".//span[@class='break-all']"
                ])
                
                if not file_name_element:
                    continue
                    
                file_name = file_name_element.get_attribute("title") if file_name_element.get_attribute("title") else file_name_element.text
                
                if not file_name or not (file_name.endswith('.xlsx') or file_name.endswith('.xls') or file_name.endswith('.csv')):
                    continue
                
                date_element = self.find_element(row, [".//time", ".//p[contains(@class, 'line-clamp-2')]"])
                if not date_element:
                    continue
                    
                date_text = date_element.text.split("\n")[0]
                file_date = self.parse_date(date_text)
                
                if file_date and self.start_date <= file_date <= self.end_date:
                    files_to_download.append({
                        "row": row,
                        "name": file_name,
                        "folder": folder_category
                    })
                    print(f"Archivo en rango: {file_name}")
            except Exception as e:
                print(f"Error al procesar archivo: {e}")
        
        print(f"Se descargarán {len(files_to_download)} archivos")
        
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        
        for file_info in files_to_download:
            try:
                file_row = file_info["row"]
                file_name = file_info["name"]
                
                print(f"Descargando: {file_name}")
                
                actions = ActionChains(self.driver)
                actions.context_click(file_row).perform()
                time.sleep(0.5)
                
                download_option = self.find_element(self.driver, [
                    "//div[contains(text(), 'Descargar')]",
                    "//span[contains(text(), 'Descargar')]"
                ])
                
                if download_option and self.click_element(download_option):
                    print(f"Descarga iniciada con menú contextual")
                else:
                    checkbox = file_row.find_element(By.XPATH, ".//input[@type='checkbox']")
                    self.click_element(checkbox)
                    time.sleep(0.5)
                    
                    download_button = self.find_element(self.driver, [
                        "//button[contains(@aria-describedby, 'Descargar')]",
                        "//button[@aria-label='Descargar']",
                        "//button[contains(text(), 'Descargar')]"
                    ])
                    
                    if download_button and self.click_element(download_button):
                        print(f"Descarga iniciada con botón Descargar")
                    else:
                        print(f"No se pudo descargar {file_name}")
                        continue
                
                time.sleep(5)
                
                for i in range(20):
                    source_path = os.path.join(download_dir, file_name)
                    if os.path.exists(source_path) and os.path.getsize(source_path) > 0:
                        time.sleep(1)
                        break
                    time.sleep(0.5)
                
                if os.path.exists(source_path):
                    dest_path = os.path.join(target_dir, file_name)
                    shutil.move(source_path, dest_path)
                    print(f"Archivo movido a: {dest_path}")
                else:
                    print(f"Archivo no encontrado en: {source_path}")
                    
                try:
                    if checkbox.is_selected():
                        self.click_element(checkbox)
                except:
                    pass
                    
            except Exception as e:
                print(f"Error descargando {file_info['name']}: {e}")
        
        print(f"Completado procesamiento de {len(files_to_download)} archivos")

    def run(self):
        """Método principal que ejecuta todo el flujo de automatización para descargar archivos de múltiples carpetas"""
        for folder in self.target_folders:
            folder_dir = os.path.join(self.base_download_dir, folder.replace(" - ", "_").replace(" ", "_"))
            os.makedirs(folder_dir, exist_ok=True)
        
        self.driver = self.setup_driver()
        
        try:
            self.login()
            
            for folder_name in self.target_folders:
                print(f"\n*** Procesando carpeta: {folder_name} ***")
                target_dir = os.path.join(self.base_download_dir, folder_name.replace(" - ", "_").replace(" ", "_"))
                
                folder_element = self.find_element(self.driver, [
                    f"//span[contains(text(), '{folder_name}')]",
                    f"//div[@role='row']//span[contains(text(), '{folder_name}')]"
                ])
                
                if not folder_element:
                    print(f"No se encontró la carpeta '{folder_name}', continuando con la siguiente...")
                    continue
                    
                self.click_element(folder_element)
                time.sleep(2)
                
                latest_subfolder = self.find_latest_subfolder()
                if latest_subfolder:
                    self.click_element(latest_subfolder["element"].find_element(By.XPATH, ".//span[@class='break-all']"))
                    time.sleep(2)
                
                self.download_files(folder_name, target_dir)
                
                self.driver.get(self.direct_link)
                time.sleep(2)
        
        except Exception as e:
            print(f"Error general: {e}")
        finally:
            time.sleep(5)
            self.driver.quit()
            
            fin = datetime.datetime.now()
            print(f"Tiempo total de ejecución: {fin - self.inicio}")

if __name__ == "__main__":
    kiteworks = KiteworksChubb()
    kiteworks.run()