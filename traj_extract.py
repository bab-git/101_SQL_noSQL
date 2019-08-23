# -*- coding: utf-8 -*-
"""
The pipeline performs data completion for cases we need the trajectory of the fails on occation

@author: Babak Hosseini
"""
print(__doc__)

import time
import os.path
import numpy as np
from datetime import datetime
import pandas as pd
import pymongo
from openpyxl import load_workbook
#from pymongo import Connection
from pymongo import MongoClient
import pprint

Mclient = MongoClient('mongodb://192.168.2.208:27018')

db = Mclient.sms
db.list_collection_names()

os.chdir('C:\\101_task')

clients = db['client']
checks = db['check']
#%%==================== Extracting trajectory data on demand
start_ind = 8    # start and end row indexes to be processed in the excell file
end_ind = 209
head_ind=7        # index of the header
excel_path = 'Checks list.xlsx' 
#book = load_workbook(excel_path)   
if os.path.isfile(excel_path):
    print('Reading data from the excel sheet...')
else:
    print("file not found") 
    
headers = pd.read_excel(excel_path, header = head_ind,nrows = 0 )
#np.where(fails_temp.columns=='Label')
#label_cl=list(fails_temp.columns).index('Label')
fails_select = pd.read_excel(excel_path, skiprows = start_ind-1,  nrows = end_ind-start_ind+1)
fails_select=fails_select.loc[fails_select['Label']==4]
fails_select=fails_select.fillna('')
#fails_select=fails_select.loc[fails_select['last_fail']!='']
fails_select=fails_select.reset_index(drop = True)

get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
#out_ind = get_indexes(4,label_list['Label'])
#excell_ind = np.array(out_ind) +start_ind
# %% Extraction loop
row_ind = 0
while row_ind < len(fails_select.index):
    start_time, end_time, checkid, deviceid = \
        fails_select.loc[row_ind,['servertime','last_fail','checkid', 'deviceid']]
    if end_time=='' : end_time = datetime(2019,7,31,23,59,59)
    deviceid , checkid = int(deviceid), str(int(checkid))
    print(('Getting checks for trajectoty: %d / %d') % (row_ind+1,len(fails_select.index)))
#    end_time = fails_select.loc[row_ind,'last_fail']
#    checkid = fails_select.loc[row_ind,'checkid']
#    deviceid = fails_select.loc[row_ind,'deviceid']
    results = checks.find(
                {
                    "servertime":
                    {
                                    "$gte": start_time,
                                    "$lte": end_time
                                    },    
                    "deviceid":deviceid,
                    "checkid": checkid
                }
                )    
    results = list(results)
#    len(check_results)
    check_SQL=pd.DataFrame(results, columns = ['checkstatus','description',
                                                         'servertime','extra','dsc247',
                                                         'deviceid','consecutiveFails','checkid']).sort_values(by = 
                                                        'servertime')#, ascending = False)
#                                                        ['checkid','servertime'])#, ascending = False)   
    temp = fails_select.loc[row_ind,['device_name','client_name','site_name','Type']]
    check_SQL[['device_name','client_name','site_name','Type']] = check_SQL.apply(lambda row: temp, axis = 1)      
    check_SQL_last = check_SQL[['device_name','Type','checkstatus',
                                    'description','servertime',
                                    'client_name','site_name','extra',
                                    'dsc247','deviceid','checkid','consecutiveFails']]    
    
    print('Saving', len(check_SQL_last), 'extracted trajectory to the SQL table...')   
    excel_path = 'Check_trajectory.xlsx'
    if not os.path.isfile(excel_path):
        check_SQL_last.to_excel(excel_path, index = False)
    else: # appending to the excell file
        book = load_workbook(excel_path)
        last_row = book['Sheet1'].max_row        
        writer = pd.ExcelWriter(excel_path, engine='openpyxl')        
#        writer = pd.ExcelWriter(excel_path)
#        check_SQL_last.to_excel(writer)
#        writer.save()        
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        check_SQL_last.to_excel(writer, startrow = last_row+1,index = False, header = False)
        writer.save()
    print("""
          =========== tabel saved =====
          ============================="""
          )
    row_ind +=1
print("""
      =========== All trajectories are saved in the excell file =====
      ============================================================="""
      )    
#break
#%%==================== Check the running operations
a=db.current_op()
print(len(a['inprog'])-1,'operation is still running')