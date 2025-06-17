# -*- coding: utf-8 -*-
"""
@author: Ronal.Barberi
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WebScraping_Chrome:

    @staticmethod
    def Webdriver_ChrDP(driver_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    
    @staticmethod
    def Webdriver_ChrDP_DP(driver_path, download_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    
    @staticmethod
    def Webdriver_ChrPP_DP(profile_path, driver_path):
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    
    @staticmethod
    def WebScraping_Acces(driver, link):
        driver.get(link)
    
    @staticmethod
    def WebScraping_Keys(driver, xpath_, s_keys):
        keys = driver.find_element(By.XPATH, xpath_)
        keys.send_keys(s_keys)
    
    @staticmethod
    def WebScraping_KeysCSS(driver, xpath_, s_keys):
        keys = driver.find_element(By.CSS_SELECTOR, xpath_)
        keys.send_keys(s_keys)
    
    @staticmethod
    def WebScraping_Nav(driver, xpath_):
        button = driver.find_element(By.XPATH, xpath_)
        button.click()

    @staticmethod
    def WebScraping_Cle(driver, xpath_):
        button = driver.find_element(By.XPATH, xpath_)
        button.clear()
    
    @staticmethod
    def WebScraping_NavCSS(driver, xpath_):
        button = driver.find_element(By.CSS_SELECTOR, xpath_)
        button.click()
    
    @staticmethod
    def WebScraping_Wait(driver, wait, xpath_):
        wait_xpath = xpath_
        WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.XPATH, wait_xpath)))
    
    @staticmethod
    def WebScraping_Wait_ID(driver, wait, id_):
        WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.ID, id_))
        )


    @staticmethod
    def WebScraping_Wait_Clickeable(driver, wait, xpath_):
        WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.XPATH, xpath_)))
        return driver.find_element(By.XPATH, xpath_)

    
    @staticmethod
    def WebScraping_Select(driver, name_id, text):
        source = driver.find_element(By.NAME , name_id)
        source_select = Select(source)
        source_select.select_by_visible_text(f'{text}')


    @staticmethod
    def WebScraping_Select_Xpath(driver, xpath, values):
        """
        Selecciona varias opciones de un <select> mediante XPath.
        
        Parámetros:
        - driver: instancia de Selenium WebDriver
        - xpath: XPath del <select> o <option>
        - values: lista de valores o textos visibles de las opciones
        """
        try:
            element = driver.find_element(By.XPATH, xpath)
            select = Select(element)

            if select.is_multiple:
                select.deselect_all()  # Limpia antes de seleccionar

            for value in values:
                try:
                    select.select_by_value(value)
                except:
                    select.select_by_visible_text(value)

            print(f"[INFO] Seleccionadas las opciones: {values}")
        except Exception as e:
            print(f"[ERROR] No se pudo seleccionar las opciones '{values}' en xpath '{xpath}'")
            raise e


