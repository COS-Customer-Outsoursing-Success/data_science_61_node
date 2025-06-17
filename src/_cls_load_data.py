# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 15:32:22 2023

@author: raul.hernandez
"""


import pandas as pd
import sqlalchemy as sqa
from sqlalchemy import create_engine as ce
from sqlalchemy.dialects.mysql import insert

class LoadDataframePandas:
    
    def __init__(self , varSchema , varTable , objMySqlConnection , varDataframeResult , varNombreBaseOperacion):
        self.varSchema = varSchema
        self.varTable = varTable
        self.objMySqlConnection = objMySqlConnection
        self.varDataframeResult = varDataframeResult
        self.varNombreBaseOperacion = varNombreBaseOperacion


    def funInsertDFNotTruncate(objConection, varDfUpdate, varSchema, varTable): 
        
        def funInsertIgnore(table, conn, keys, data_iter):
            insert_stmt = insert(table.table).values(list(data_iter)) 
            ignore_stmt = insert_stmt.prefix_with('IGNORE')
            conn.execute(ignore_stmt)
            
        varDfUpdate.to_sql(varTable, objConection, varSchema, if_exists='append', index=False, method=funInsertIgnore, chunksize=10000)
        print(f'Se han Insertado {varDfUpdate.shape[0]} registros nuevos en {varTable}')
        
    
    def funMainLoadDataServer(objMySqlConnection , varTable , varSchema , varDataframeFinal , varDataframeServer ):
         
        def funInspectSchema(objMySqlConnection , varTable , varSchema):
            
            varMySqlInspect = sqa.inspect(objMySqlConnection)
            varInspectResult = varMySqlInspect.has_table(varTable ,schema= varSchema )
            return varInspectResult
        
        
        def funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable):
            
            
            def funCompareColumns(varDataframeFinal , varDataframeServer):
                varDataframeFinalColumns = varDataframeFinal.columns.to_list()
                varDataframeServerColumns = varDataframeServer.columns.to_list()
                varListDifferenceColumns = set(varDataframeFinalColumns).difference(set(varDataframeServerColumns))
                return varListDifferenceColumns
            
            
            def funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable ):
                
                def funExecuteQueryAdd(objMySqlConnection , varListAlterTableColumns):
                    try:
                        objMySqlConnection.execute(varListAlterTableColumns)
                    except:
                        print('The column {0} is duplicate.'.format(varListAlterTableColumns))
                
                
                varListAlterTableColumns = ['ALTER TABLE `{0}`.`{1}` ADD COLUMN `{2}` VARCHAR(64)'.format(varSchema , varTable , i ) for i in varListColumnsToAdd]
                varExecuteAlterTableColumns = [funExecuteQueryAdd(objMySqlConnection , i) for i in varListAlterTableColumns]
                return 
                
            
            varListColumnsToAdd : list = funCompareColumns(varDataframeFinal , varDataframeServer)
            varListAlterTableColumns : list = funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable)
            
            
            return
                
        
        def funLoadDataframeServer(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = False , method = funInsertOnDuplicate , chunksize=5000)
            
            
        def funLoadDataframeServerIndex(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = True , method = funInsertOnDuplicate , chunksize=5000)
         
        
        def funDeleteDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'delete from `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        def funDeleteDataServerNombreBaseOperacion(objMySqlConnection , varTable , varSchema , varNombreBaseOperacion):
            varDeleteQuery = 'delete from `{0}`.`{1}` where nombre_base_operacion = "{2}"'.format(varSchema , varTable , varNombreBaseOperacion)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
            
        
        def funTruncateDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'truncate table `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        varInspectServer = funInspectSchema(objMySqlConnection , varTable , varSchema)
        
        
        funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable)
        
        
        funTruncateDataServer(objMySqlConnection , varTable , varSchema )
        
        
        funLoadDataframeServer(objMySqlConnection , varDataframeFinal , varTable , varSchema )
        

        return 
    
    def funMainLoadDataServerNotTruncate(objMySqlConnection , varTable , varSchema , varDataframeFinal , varDataframeServer ):
        
         
        
        def funInspectSchema(objMySqlConnection , varTable , varSchema):
            
            
            varMySqlInspect = sqa.inspect(objMySqlConnection)
            varInspectResult = varMySqlInspect.has_table(varTable ,schema= varSchema )
            return varInspectResult
        
        
        def funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable):
            
            
            def funCompareColumns(varDataframeFinal , varDataframeServer):
                varDataframeFinalColumns = varDataframeFinal.columns.to_list()
                varDataframeServerColumns = varDataframeServer.columns.to_list()
                varListDifferenceColumns = set(varDataframeFinalColumns).difference(set(varDataframeServerColumns))
                return varListDifferenceColumns
            
            
            def funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable ):
                
                def funExecuteQueryAdd(objMySqlConnection , varListAlterTableColumns):
                    try:
                        objMySqlConnection.execute(varListAlterTableColumns)
                    except:
                        print('The column {0} is duplicate.'.format(varListAlterTableColumns))
                
                
                varListAlterTableColumns = ['ALTER TABLE `{0}`.`{1}` ADD COLUMN `{2}` VARCHAR(64)'.format(varSchema , varTable , i ) for i in varListColumnsToAdd]
                varExecuteAlterTableColumns = [funExecuteQueryAdd(objMySqlConnection , i) for i in varListAlterTableColumns]
                return 
                
            
            varListColumnsToAdd : list = funCompareColumns(varDataframeFinal , varDataframeServer)
            varListAlterTableColumns : list = funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable)
            
            
            return
                
        
        def funLoadDataframeServer(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = False ,  method = funInsertOnDuplicate , chunksize=5000)
            
            
        def funLoadDataframeServerIndex(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_ignore(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = True , method = funInsertOnDuplicate , chunksize=5000)
         
        
        def funDeleteDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'delete from `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        def funDeleteDataServerNombreBaseOperacion(objMySqlConnection , varTable , varSchema , varNombreBaseOperacion):
            varDeleteQuery = 'delete from `{0}`.`{1}` where nombre_base_operacion = "{2}"'.format(varSchema , varTable , varNombreBaseOperacion)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
            
        
        def funTruncateDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'truncate table `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        varInspectServer = funInspectSchema(objMySqlConnection , varTable , varSchema)
        
        
        funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable)
        
        
        funLoadDataframeServer(objMySqlConnection , varDataframeFinal , varTable , varSchema )
        
        
        
        
        
    def funMainLoadDataServerNotTruncateNF(objMySqlConnection , varTable , varSchema , varDataframeFinal , varDataframeServer ):
        
         
        
        def funInspectSchema(objMySqlConnection , varTable , varSchema):
            
            
            varMySqlInspect = sqa.inspect(objMySqlConnection)
            varInspectResult = varMySqlInspect.has_table(varTable ,schema= varSchema )
            return varInspectResult
        
        
        def funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable):
            
            
            def funCompareColumns(varDataframeFinal , varDataframeServer):
                varDataframeFinalColumns = varDataframeFinal.columns.to_list()
                varDataframeServerColumns = varDataframeServer.columns.to_list()
                varListDifferenceColumns = set(varDataframeFinalColumns).difference(set(varDataframeServerColumns))
                return varListDifferenceColumns
            
            
            def funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable ):
                
                def funExecuteQueryAdd(objMySqlConnection , varListAlterTableColumns):
                    try:
                        objMySqlConnection.execute(varListAlterTableColumns)
                    except:
                        print('The column {0} is duplicate.'.format(varListAlterTableColumns))
                
                
                varListAlterTableColumns = ['ALTER TABLE `{0}`.`{1}` ADD COLUMN `{2}` VARCHAR(64)'.format(varSchema , varTable , i ) for i in varListColumnsToAdd]
                varExecuteAlterTableColumns = [funExecuteQueryAdd(objMySqlConnection , i) for i in varListAlterTableColumns]
                return 
                
            
            varListColumnsToAdd : list = funCompareColumns(varDataframeFinal , varDataframeServer)
            varListAlterTableColumns : list = funAddColumsServer(objMySqlConnection , varListColumnsToAdd , varSchema , varTable)
            
            
            return
                
        
        def funLoadDataframeServer(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = False , method = funInsertOnDuplicate , chunksize=5000)
            
            
        def funLoadDataframeServerIndex(objMySqlConnection , varDataframeResult , varTable , varSchema ): 
            
            def funInsertOnDuplicate(table, conn, keys, data_iter):
                insert_stmt = insert(table.table).values(list(data_iter)) 
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_ignore(insert_stmt.inserted)
                conn.execute(on_duplicate_key_stmt) 
                
            varDataframeResult.to_sql( varTable ,objMySqlConnection , varSchema , if_exists = 'append', index = True , method = funInsertOnDuplicate , chunksize=5000)
         
        
        def funDeleteDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'delete from `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        def funDeleteDataServerNombreBaseOperacion(objMySqlConnection , varTable , varSchema , varNombreBaseOperacion):
            varDeleteQuery = 'delete from `{0}`.`{1}` where nombre_base_operacion = "{2}"'.format(varSchema , varTable , varNombreBaseOperacion)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
            
        
        def funTruncateDataServer(objMySqlConnection , varTable , varSchema ):
            varDeleteQuery = 'truncate table `{0}`.`{1}`'.format(varSchema , varTable)
            try:
                objMySqlConnection.execute(varDeleteQuery)
            except:
                objMySqlConnection = objMySqlConnection 
                
        
        varInspectServer = funInspectSchema(objMySqlConnection , varTable , varSchema)
        
        
        funAddColumns(objMySqlConnection , varInspectServer , varDataframeFinal , varDataframeServer, varSchema , varTable)
        
        
        funLoadDataframeServer(objMySqlConnection , varDataframeFinal , varTable , varSchema )
    

        return 
            
#%%
class LogDocumentsLoaded:
    
    def __init__(self):
        for key, value in args.items():
            setattr(self, key, value)
            
    
        
        
if __name__=='__main__':
    
    args = {'path':''}
