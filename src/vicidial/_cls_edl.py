import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from web_scraping._cls_webscraping import WebScraping_Chrome

current_folder = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_folder))
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

class EdlVicidial:
    def __init__(self, user_vcdl=None, pass_vcdl=None, server_vcdl=None, campaigns=None, archivo_edl=None):
       
        # -- Config driver path -- 
        self.path_home = str(Path.home())
        self.driver_path = os.path.join(
            self.path_home, 
            'Documents',
            'chromedriver.exe'
        )
      
        # -- Config Vicidial -- 
        self.user_vcdl = user_vcdl 
        self.pass_vcdl = pass_vcdl
        self.server_vcdl = server_vcdl
        self.campaigns = [campaigns] if isinstance(campaigns, str) else (campaigns or [])
        self.archivo_edl = archivo_edl
        
        self.url = (
            f"http://{self.user_vcdl}:{self.pass_vcdl}@"
            f"{self.server_vcdl}/vicidial/realtime_report.php?"
            f"RR=4&DB=0&group={','.join(self.campaigns) if self.campaigns else 'ALL-ACTIVE'}#"
        )
        print(f"Accediendo a URL: {self.url.split('@')[-1]}")  # Print URL without credentials

        # -- Config Rutas -- 
        campaign_dir = '_'.join(self.campaigns) if self.campaigns else 'ALL-ACTIVE'

        self.ruta_img = os.path.join(project_root, 'data', 'img', 'edl_vcdl', campaign_dir)
        os.makedirs(self.ruta_img, exist_ok=True)

    def _select_campaign(self, driver, campaña):
        
        try:
            boton_campañas_xpath = "//a[@onclick=\"showDiv('campaign_select_list');\"]"
            WebScraping_Chrome.WebScraping_Wait(driver, 150, boton_campañas_xpath)
            WebScraping_Chrome.WebScraping_Nav(driver, boton_campañas_xpath)
            
            menu_desplegable_xpath = "//select[@name='groups[]']"
            WebScraping_Chrome.WebScraping_Wait(driver, 150, menu_desplegable_xpath)

            opcion_campaña_xpath = f"//select[@name='groups[]']/option[contains(text(), '{campaña}')]"
            WebScraping_Chrome.WebScraping_Wait(driver, 150, opcion_campaña_xpath)
            elemento_opcion = driver.find_element(By.XPATH, opcion_campaña_xpath)
            
            if not elemento_opcion.is_selected():
                elemento_opcion.click()
                print(f"✅ Campaña seleccionada: {campaña}")
            else:
                print(f"ℹ️ Campaña ya estaba seleccionada: {campaña}")

        except Exception as e:
            print(f"[ERROR] No se pudo seleccionar la campaña '{campaña}': {str(e)}")
            raise
    
    def cargar_vcdl(self):
        resultados = []

        for campaña in self.campaigns:
            url_campaña = (
                f"http://{self.user_vcdl}:{self.pass_vcdl}@"
                f"{self.server_vcdl}/vicidial/realtime_report.php?"
                f"RR=4&DB=0&group={campaña}#"
            )
            print(f"\n[INFO] Procesando campaña: {campaña}")
            print(f"[INFO] URL: {url_campaña.split('@')[-1]}")

            try:
                driver = WebScraping_Chrome.Webdriver_ChrDP(self.driver_path)
                WebScraping_Chrome.WebScraping_Acces(driver, url_campaña)
                WebScraping_Chrome.WebScraping_Wait(driver, 30, "//body")
                print("Vicidial page loaded successfully")

                try:
                        boton_campañas_xpath = "//a[@onclick=\"showDiv('campaign_select_list');\"]"
                        WebScraping_Chrome.WebScraping_Wait(driver, 150, boton_campañas_xpath)
                        WebScraping_Chrome.WebScraping_Nav(driver, boton_campañas_xpath)
                        
                        menu_desplegable_xpath = "//select[@name='groups[]']"
                        WebScraping_Chrome.WebScraping_Wait(driver, 150, menu_desplegable_xpath)

                        opcion_campaña_xpath = f"//select[@name='groups[]']/option[contains(text(), '{campaña}')]"
                        WebScraping_Chrome.WebScraping_Wait(driver, 150, opcion_campaña_xpath)
                        elemento_opcion = driver.find_element(By.XPATH, opcion_campaña_xpath)
                        
                        if not elemento_opcion.is_selected():
                            elemento_opcion.click()
                            print(f"✅ Campaña seleccionada: {campaña}")
                        else:
                            print(f"ℹ️ Campaña ya estaba seleccionada: {campaña}")

                except Exception as e:
                    print(f"[ERROR] No se pudo seleccionar la campaña '{campaña}': {str(e)}")
                    raise

#                self._select_campaign(driver, campaña)

                WebScraping_Chrome.WebScraping_Wait(driver, 30, '//*[@id="report_display_type"]')            
                WebScraping_Chrome.WebScraping_Keys(driver, '//*[@id="report_display_type"]', 'HTML')
                WebScraping_Chrome.WebScraping_Wait(driver, 30, "//input[@type='button' and @value='SUBMIT']")
                WebScraping_Chrome.WebScraping_Nav(driver, "//input[@type='button' and @value='SUBMIT']")
                time.sleep(3)

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'realtime_calls_table'})
                if table is None:
                    print(f"[ADVERTENCIA] No se encontró tabla para la campaña: {campaña}")
                    continue

                data = []

                # Llamadas
                call_labels = table.find_all('font', {'class': 'realtime_img_text'})[:6]
                call_values = table.find_all('font', {'style': 'font-family:HELVETICA;font-size:18;color:white;font-weight:bold;'})[:6]

                for label, value in zip(call_labels, call_values):
                    data.append({
                        'Categoría': label.get_text(strip=True),
                        'Valor': value.get_text(strip=True),
                        'Tipo': 'Llamadas'
                    })

                # Agentes
                agent_labels = table.find_all('font', {'class': 'realtime_img_text'})[6:]
                agent_values = table.find_all('font', {'style': True})[6:]
                agent_values = [v for v in agent_values if v.get_text(strip=True).isdigit()][:6]

                for label, value in zip(agent_labels, agent_values):
                    data.append({
                        'Categoría': label.get_text(strip=True),
                        'Valor': value.get_text(strip=True),
                        'Tipo': 'Agentes'
                    })

                df = pd.DataFrame(data)
                print(df)
    
                filename = os.path.join(
                    self.ruta_img,
                    f"EDL_{campaña}_{timestamp}.xlsx"
                )
                df.to_excel(filename, index=False)
                print(f"[OK] Datos guardados para campaña '{campaña}' en {filename}")
                resultados.append(filename)

            except TimeoutException:
                print(f"[ERROR] Timeout para la campaña: {campaña}")
            except NoSuchElementException as e:
                print(f"[ERROR] Elemento no encontrado en campaña '{campaña}': {str(e)}")
            except Exception as e:
                print(f"[ERROR] Error inesperado en campaña '{campaña}': {str(e)}")
            finally:
                if 'driver' in locals():
                    driver.quit()

        return resultados

