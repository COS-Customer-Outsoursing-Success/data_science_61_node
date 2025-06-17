# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 13:40:15 2024

@author: Ronal.Barberi
"""

#%% Imported libraries

import os
import re
import time
import psutil
import pyperclip
from PIL import ImageGrab
import win32com.client as win32
from unidecode import unidecode
from datetime import datetime, timedelta
from _cls_webscraping import WebScraping_Chrome as ws
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


#%% Create Class

class Excel_Img:
    def __init__(self, excel_file_path, rangos, image_folder, whatsapp_group):
        self.excel_file_path = excel_file_path
        self.rangos = rangos
        self.image_folder = image_folder
        self.whatsapp_group = whatsapp_group
        self.xlSheetVisible = -1
        self.xlSheetHidden = 0
        self.xlSheetVeryHidden = 2
        self.xlBitmap = 2
    
    def kill_proccess(self):
        print("¡Los arcivo Excel se cerraran en 5 segundos!")
        time.sleep(5)
        print("Se han cerrado todos los archivos Excel abiertos, continuando con el proceso.")
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'EXCEL.EXE':
                psutil.Process(proc.info['pid']).terminate()
    
    def ScreenshotExcel(self):
        print("Abriendo archivo")
        excel_app = win32.DispatchEx("Excel.Application")
        excel_app.DisplayAlerts = False
        excel_app.Visible = False
        workbook = excel_app.workbooks.open(self.excel_file_path)
        print("Actualizando consultas")
        workbook.RefreshAll()
        excel_app.CalculateUntilAsyncQueriesDone()
        print("Actualizando tablas dinamicas")
        for sheet in workbook.Sheets:
            for pivot_table in sheet.PivotTables():
                pivot_table.RefreshTable()
                print(f"Actualizando {pivot_table}")
                time.sleep(2)
                
        # Iterate through all sheets and capture images
        print("Capture images")
        for sheet in workbook.Sheets:
            if sheet.Visible == self.xlSheetVisible:
               sheet_name = sheet.Name
               if sheet_name in self.rangos:
                   try:
                       range_ = sheet.Range(self.rangos[sheet_name])
                       range_validacion = sheet.Range('A1:A1')
                       if range_validacion.Cells(1, 1).Value is not None and range_validacion.Cells(1, 1).Value > 0:
                          range_.CopyPicture(Format=self.xlBitmap)
                          time.sleep(2)
                          captura = ImageGrab.grabclipboard()
                          
                          # Save the image with a name based on the sheet name
                          pattern = r'[A-Za-z0-9]+'
                          sheet_name = sheet_name.replace('_','')
                          sheet_name = re.findall(pattern, sheet_name)[0]
                          sheet_name = unidecode(sheet_name)
                          print("Capture: ", sheet_name)
                          time.sleep(2)
                          image_path = os.path.join(self.image_folder, f"{self.whatsapp_group}_{sheet_name}.jpg" )
                          time.sleep(2)
                          captura.save(image_path)
                          pyperclip.copy('')
                          time.sleep(3)
                       else:
                          print(f"No data found in A1 of {sheet_name}. Image not captured.")
                   except Exception as n:
                      print(f"Error copy: {n}")
                      
        workbook.Save()
        workbook.Close(False)
        excel_app.Quit()
        print("Close workbook")
        del excel_app
    
    def get_image_paths(self):
        return self.image_paths
    
    def main(self):
        self.kill_proccess()
        self.ScreenshotExcel()


class SeendMsg_Wpp:
    def __init__(self, driver_path, profile_path, whatsapp_group, text_wpp, image_folder):
        self.driver_path = driver_path
        self.profile_path = profile_path
        self.whatsapp_group = whatsapp_group
        self.text_wpp = text_wpp
        self.image_folder = image_folder
    
    def Interval_Current(self):
        interval = datetime.now()
        interval -= timedelta(minutes=interval.minute % 30, seconds=interval.second)
        interval = interval.strftime('%d/%m/%Y - %H:%M:%S')
        return interval
    
    def Open_seend_img(self):
        interval = self.Interval_Current()
        print(f"Enviando PDC a {self.whatsapp_group}, a corte {interval}.")
        driver = ws.Webdriver_ChrPP_DP(self.profile_path, self.driver_path)
        ws.WebScraping_Acces(driver, "https://web.whatsapp.com")
        ws.WebScraping_Wait(driver, 300, "//*[@id='side']/div[1]/div/div[2]/div[2]/div/div[1]/p")
        ws.WebScraping_Keys(driver, "//*[@id='side']/div[1]/div/div[2]/div[2]/div/div[1]/p", self.whatsapp_group)
        time.sleep(1)
        ws.WebScraping_Keys(driver, "//*[@id='side']/div[1]/div/div[2]/div[2]/div/div[1]/p", Keys.RETURN)
        time.sleep(3)
        for clave, valor in self.text_wpp:
            ws.WebScraping_Nav(driver, "//*[@id='main']/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div")
            time.sleep(1)
            try:
                print(f"Buscando archivo en la ruta: {self.image_folder}\\{self.whatsapp_group}_{clave}.jpg")
                ws.WebScraping_Keys(driver, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]', f"{self.image_folder}\\{self.whatsapp_group}_{clave}.jpg")
                time.sleep(3)
                ws.WebScraping_Keys(driver, '//div[@title="Escribe un mensaje"]', f"{valor} a corte {interval}")
                time.sleep(1)
                ws.WebScraping_Keys(driver, '//div[@title="Escribe un mensaje"]', Keys.ENTER)
            except:
                print(f"{clave}, no fue encontrado en la ruta: {self.image_folder}\\{self.whatsapp_group}_{clave}.jpg")
                pass
        time.sleep(30)
        driver.close()
        print("PDC enviado.")
    
    def main(self):
        self.Open_seend_img()


#%% Use Class
"""
current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder)

if __name__ == "__main__":
    excel_file_path= os.path.join(parent_folder, 'data', 'informes', '01_pdc_laika_ventas.xlsx')
    rangos= {
        "PuntoDeControlLaikaVentas":"B2:O46"}
    image_folder= os.path.join(parent_folder, 'data')
    whatsapp_group= "Data Science Laika"
    Excl_img = Excel_Img(excel_file_path, rangos, image_folder, whatsapp_group)
    Excl_img.main()

    driver_path= os.path.join(parent_folder, 'config', 'chromedriver.exe')
    profile_path = "user-data-dir=C:\\Command_Center\\Profile"
    link_ = "https://web.whatsapp.com"
    SeendWpp = SeendMsg_Wpp(driver_path, profile_path, link_, whatsapp_group, rangos, image_folder)
    SeendWpp.main()
"""
