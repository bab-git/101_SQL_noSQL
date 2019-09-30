"""
Created on Tue Jul 30 13:55:19 2019

The pipeline brings not annotated cases or missed cases forward (higher rows) 
int the google sheet to be annotated earlier.

@author: Babak Hosseini
"""
print(__doc__)

from  mongo_classifier import H_annot
import pickle
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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import shutil
from git import Repo
from gspread_pandas import Spread

Mclient = MongoClient('mongodb://192.168.2.208:27018')

db = Mclient.sms
db.list_collection_names()

os.chdir('C:\\SYNX')

clients = db['client']
checks = db['check']


#%%===========================================================================
#==================== Bringing not annotated cases or missed cases forward for annotation
#===========================================================================    
modif_code = 'green'  # Enter this code if you really want to modify the spreadsheet
get_code = input('''
You are about to modify the existing "google spread sheet"!! 
--------------------
You can also rename the target sheet by "g_sheet_name" 
if you want to work on a different data set
However, you need to create the new google sheet online
and share it with the API key first!
--------------------
If you know what you are doing, please enter the pass-code! ;-)
Pass-code:''')
if get_code != modif_code:
#    print('dsadsa')
    raise ValueError('''Wrong code! 
                Cannot continue!!''')

print('''If anything goes wrong, please check the google sheet history 
      to get of the google sheet and check_DB before modification...''')


head_ind = 8

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Checks list").sheet1
sheet_g = Spread("Checks list")    
sheet_g.open_sheet("Sheet1", create=False)

headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
SQL_cpy = pd.DataFrame(all_values)
SQL_cpy.to_excel('check_back_%s.xlsx' %(str(datetime.now().timestamp())[:10]), index = False)

check_SQL  = pd.DataFrame(all_values, columns = headers)    

label_list = sheet.col_values(headers.index('Label')+1)
labeled_rows = list(filter(lambda x: label_list[x] != '', range(head_ind,len(label_list))))
labeled_rows = [int(x) for x in labeled_rows]
annot_checks = check_SQL.loc[labeled_rows,'description'].unique()
all_checks = check_SQL.loc[range(head_ind,len(check_SQL)),'description'].unique()
rest_checks = check_SQL.loc[range(labeled_rows[len(labeled_rows)-1],len(check_SQL)),'description'].unique()
last_annot = labeled_rows[len(labeled_rows)-1]+1
    
if len(all_checks) > len(annot_checks):  # need to bring forward not annotated checks
    moved_dv = []
    for check_i in all_checks:        
        if check_i not in annot_checks: # new check
           
            row_ck = list(check_SQL['description']).index(check_i)
            row_dv = list(check_SQL['deviceid']).index(check_SQL.loc[row_ck,'deviceid'])
            deviceid = check_SQL.loc[row_ck,'deviceid']
            
            
            if (last_annot+1) >= row_dv: # right place: after last annotation
                moved_dv.append(deviceid)
                continue

            elif deviceid in moved_dv:  # new check from already moved device
                continue   

            a = list(check_SQL.loc[range(row_dv),'deviceid'].unique())
            if a[len(a)-1] in moved_dv: # new check after another new check
                moved_dv.append(deviceid)
                continue                        
            else : # wrong place
                print('Bringing a not-annotated check forward - check:' , check_i)
                row_sql = list(check_SQL['description']).index(check_i)
                device_id = check_SQL.loc[row_sql,'deviceid']
                get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
                rows_ind = get_indexes(device_id,check_SQL['deviceid'])
                temp = check_SQL.iloc[rows_ind]
                
                rows_ind.reverse()
                for row in rows_ind:
                    sheet.delete_row(row+1)
                
                for i in range(0,len(temp)+1):
                    sheet.insert_row(list(''), index = last_annot+1)                
                sheet_g.df_to_sheet(temp, index=False, headers = False,sheet='Sheet1', start=(last_annot+2,1),  replace = False)
                
                all_values = sheet.get_all_values()
                check_SQL  = pd.DataFrame(all_values, columns = headers)
                label_list = sheet.col_values(headers.index('Label')+1)
                labeled_rows = list(filter(lambda x: label_list[x] != '', range(head_ind,len(label_list))))
                labeled_rows = [int(x) for x in labeled_rows]            
                last_annot = labeled_rows[len(labeled_rows)-1]+1
                
                moved_dv.append(temp.loc[temp.index[0],'deviceid'])

print('Samples of all new checks are brough forward')                
