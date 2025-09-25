# -*- coding: utf-8 -*-
"""
@author: Ronal Barberi
@edit: Emerson Aguilar Cruz
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
    def WebScraping_KeysCSS(driver, xpath_, s_keys):
        keys = driver.find_element(By.CSS_SELECTOR, xpath_)
        keys.send_keys(s_keys)
    
# -------------------------------------- CSS SELECTOR --------------------------------------    

    @staticmethod
    def WebScraping_NavCSS(driver, xpath_):
        button = driver.find_element(By.CSS_SELECTOR, xpath_)
        button.click()
    
    @staticmethod
    def WebScraping_GetValueCSS(driver, css_selector):
        elemento = driver.find_element(By.CSS_SELECTOR, css_selector)
        return elemento.get_attribute("value")
    # Uso:

    # valor_nombre = WebScraping_GetValue(driver, 'input[formcontrolname="user"]')
    # print(valor_nombre)

    @staticmethod
    def WebScraping_WaitCSS(driver, wait, css_selector):
        WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )

    # Uso:

    # Espera hasta que aparezca el input con formcontrolname="user"
    # WebScraping_WaitCSS(driver, 10, 'input[formcontrolname="user"]')

    @staticmethod
    def WebScraping_WaitCssMulti(driver, timeout, selectors):
        """
        Intenta esperar un selector de la lista, retorna el primero que funcione.
        """
        last_exception = None
        for selector in selectors:
            try:
                WebScraping_Chrome.WebScraping_WaitCSS(driver, timeout, selector)
                return selector  # devuelvo el que funcionó
            except Exception as e:
                last_exception = e
                continue
        raise Exception(f"Ninguno de los selectores fue encontrado: {selectors}") from last_exception


    @staticmethod
    def WebScraping_ClearCSS(driver, css_selector):
        elemento = driver.find_element(By.CSS_SELECTOR, css_selector)
        elemento.clear()
    
    # Uso:
    # WebScraping_Clear_CSS(driver, 'button[type="submit"][color="primary"]')

    @staticmethod
    def WebScraping_ClickCSS(driver, css_selector):
        elemento = driver.find_element(By.CSS_SELECTOR, css_selector)
        elemento.click()
    
    # Uso:
    # WebScraping_ClickCSS(driver, 'button[type="submit"][color="primary"]')

    @staticmethod
    def WebScraping_SendKeysCSS(driver, css_selector, key):
        elemento = driver.find_element(By.CSS_SELECTOR, css_selector)
        elemento.clear()
        elemento.send_keys(key)

    # Uso: 
    # WebScraping_SendKeysCSS(driver, 'input[formcontrolname="user"]', 'eaguilar84')

    @staticmethod
    def WebScraping_WaitTextCSS(driver, wait, css_selector, hidden_text=None):
        WebDriverWait(driver, wait).until(
            lambda d: any(
                hidden_text in el.get_attribute("textContent").strip()
                if hidden_text else True
                for el in d.find_elements(By.CSS_SELECTOR, css_selector)
            )
        )

    # Uso:
    # WebScraping_WaitLinkCSS(driver, 10, 'a.mat-list-item.mat-menu-trigger')
    # WebScraping_WaitLinkCSS(driver, 10, 'a.mat-list-item.mat-menu-trigger', 'Gestor de turno')
    # WebScraping_WaitLinkCSS(driver, 10, 'a.mat-list-item.mat-menu-trigger', 'Menú')

    @staticmethod
    def WebScraping_ClickByTextCSS(driver, css_selector, hidden_text=None):
        elementos = driver.find_elements(By.CSS_SELECTOR, css_selector)
        for el in elementos:
            texto = el.get_attribute("textContent").strip()
            if hidden_text is None or hidden_text in texto:
                el.click()
                return True
        return False

    # Uso:
    # WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-menu-trigger')
    # WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-menu-trigger', 'Gestor de turno')
    # WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-menu-trigger', 'Menú')

    @staticmethod
    def WebScraping_WaitClickableCSS(driver, wait, css_selector):
        WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
    # Uso:
    # WebScraping_Chrome.WebScraping_WaitClickableCSS(driver, 20, 'a.mat-list-item.mat-focus-indicator')
    # WebScraping_Chrome.WebScraping_ClickByTextCSS(driver, 'a.mat-list-item.mat-focus-indicator', 'Formularios')

    @staticmethod
    def WebScraping_ScrollIntoViewCSS(driver, selector):
        """
        Hace scroll hasta que el elemento localizado por CSS selector esté en vista.
        """
        elem = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        return elem
    
    # Uso:
    # WebScraping_Chrome.WebScraping_ScrollIntoViewCSS(driver, 'mat-select')

    @staticmethod
    def WebScraping_WriteCSS(driver, css_selector, texto, enter=False):
        elemento = driver.find_element(By.CSS_SELECTOR, css_selector)
        elemento.click()
        elemento.clear() if elemento.tag_name in ["input", "textarea"] else None
        elemento.send_keys(texto)
        if enter:
            from selenium.webdriver.common.keys import Keys
            elemento.send_keys(Keys.ENTER)
# -------------------------------------- XPATH --------------------------------------

    @staticmethod
    def WebScraping_Nav(driver, xpath_):
        button = driver.find_element(By.XPATH, xpath_)
        button.click()

    @staticmethod
    def WebScraping_Cle(driver, xpath_):
        button = driver.find_element(By.XPATH, xpath_)
        button.clear()

    @staticmethod
    def WebScraping_Keys(driver, xpath_, s_keys):
        keys = driver.find_element(By.XPATH, xpath_)
        keys.send_keys(s_keys)

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


