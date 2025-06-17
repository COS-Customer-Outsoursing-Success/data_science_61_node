# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 12:23:03 2023

@author: Ronal.Barberi
"""
#%% Imported libraries

from sqlalchemy import create_engine
from urllib.parse import quote

#%% Create Class

class MySQLConnector61:

    @staticmethod
    def funConectMySql(database):
        varDbms = 'mysql+mysqldb'
        varUser = "andresortiz4083"
        varHost = "172.70.7.61"
        varPort = "3306"
        varPass = quote('tNjseme,8ltX413o1eOx')
        engine = None
        db = None
        cadena = f"{varDbms}://{varUser}:{varPass}@{varHost}:{varPort}/{database}"
        engine = create_engine(cadena, pool_recycle=9600, isolation_level="AUTOCOMMIT")
        return engine
