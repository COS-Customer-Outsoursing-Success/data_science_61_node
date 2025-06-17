# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 17:28:59 2024

@author: Ronal.Barberi
"""

#%% Imported libraries

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#%% Create Class

class WebScraping_Chrome:
    
    def Webdriver_ChrDP(driver_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver

    def Webdriver_ChrDP_DP(driver_path, download_path):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        prefs = {"download.default_directory": download_path}
        options.add_experimental_option("prefs", prefs)
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver

    def Webdriver_ChrPP_DP(profile_path, driver_path):
        options = webdriver.ChromeOptions()
        options.add_argument(profile_path)
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver
    
    def WebScraping_Acces(driver, link):
        driver.get(link)
    
    def WebScraping_Keys(driver, xpath_, s_keys):
        keys = driver.find_element(By.XPATH, xpath_)
        keys.send_keys(s_keys)
    
    def WebScraping_KeysCSS(driver, xpath_, s_keys):
        keys = driver.find_element(By.CSS_SELECTOR, xpath_)
        keys.send_keys(s_keys)
    
    def WebScraping_Nav(driver, xpath_):
        button = driver.find_element(By.XPATH, xpath_)
        button.click()
    
    def WebScraping_NavCSS(driver, xpath_):
        button = driver.find_element(By.CSS_SELECTOR, xpath_)
        button.click()
    
    def WebScraping_Wait(driver, wait, xpath_):
        wait_xpath = xpath_
        WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.XPATH, wait_xpath)))
    
    def WebScraping_Select(driver, name_id, text):
        source = driver.find_element(By.NAME , name_id)
        source_select = Select(source)
        source_select.select_by_visible_text(f'{text}')
