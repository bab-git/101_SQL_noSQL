"""
Created on Tue Jul 30 13:55:19 2019

The pipeline filters the already extracted mongoDB data in the google spread sheet
based on the hand-coded annotation list (H-annot).

check_extraction.sav : The file that the hand-coded filtered data is stored.


@author: Babak Hosseini
"""
print(__doc__)

#from mongo_classifier import H_annot, class_code
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
#==================== Updating g-sheet based on the short-list  (H-annot)
#===========================================================================    
# %%  safety check!
modif_code = 'green'  # Enter this code if you really want to modify the spreadsheet
get_code = input('''
You are about to modify the existing "google spread sheet"
and the "check_extraction.sav" file!! 
--------------------
You can also rename the target sheet and save file by "g_sheet_name" and "load_file"
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

print('''If anything goes wrong, please check the google sheet and the git history 
      to get of the google sheet and check_DB before modification...''')
   

load_file = 'check_extraction.sav'
loaded_data = pickle.load( open(load_file, "rb" ))
check_DB = loaded_data['check_DB']

#-----git push
if os.path.isfile(load_file):
    repo = Repo(os.getcwd())
    repo.index.add([save_file])
    repo.index.commit("backup of check_DB before modification")
    origin = repo.remotes.origin
    origin.push()
    

head_ind=8        # index of the header
#label_col = 14

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Checks list").sheet1
#sheet2 = client.open("temp2").sheet1


#fails_select = sheet.row_values(8)
headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()

sheet_checks  = pd.DataFrame(all_values, columns = headers)

i_check = 0
#  %%
while i_check< len(sheet_checks):

    g_rmd = 0
    DB_rmd = 0
    device_name = sheet_checks['device_name'][i_check]
    if device_name == '':
        i_check +=1
        continue
    checkname = sheet_checks['description'][i_check]
    extra = sheet_checks['extra'][i_check]
    pr = H_annot(checkname,extra)
    
    if pr == 'ignore': 
        print ('Row %d: Removing from google sheet' %(i_check+1))

    if pr != 'ND': #(pr=='nH')|(pr=='H'): # check-definite label H/N/Nan case
        print ('Row %d: Transfering an %s label to checkDB' %(i_check+1,pr))
        
        g_row = sheet.row_values(i_check+1)
        SQL_row = sheet_checks.iloc[i_check].values.tolist()
        SQL_row [13:16]= list(filter(lambda x: x != '', SQL_row[13:16]))
        
        if g_row != SQL_row:
            raise ValueError('SQL is not syncronized with google sheet \n update the SQL table from google-sheet')
        
        DB_col_list = check_DB.columns;
        
        deviceid = int(sheet_checks.loc[i_check,'deviceid'])

        checkid = sheet_checks.loc[i_check,'checkid']
        time =  datetime.strptime(sheet_checks.loc[i_check,'servertime'], '%Y-%m-%d %H:%M:%S')
        
        dev_ind = check_DB['deviceid'] == deviceid
        chk_ind = check_DB['checkid'] == checkid
        tm_ind = check_DB['servertime'] > time
        
        if len(check_DB.loc[dev_ind].index) == 0:
            ind_add = len(check_DB) # to the end of list
        elif len(check_DB.loc[dev_ind & chk_ind].index) == 0:
            ind_add = check_DB.loc[dev_ind].index[0]-1  # to the top of device list
        elif len(check_DB.loc[dev_ind & chk_ind & tm_ind ].index) == 0:
            ind_add = check_DB.loc[dev_ind & chk_ind].index[0]-1  # to the top of device-check list
        else:            
            ind_add = check_DB.loc[dev_ind & chk_ind & tm_ind ].index[0]-1  # after the device-check happened before this one

                    
        #--------- update check_DB                
        if ind_add == -1:
            ind_add =0
        check_DB1 = pd.DataFrame(check_DB.iloc[:ind_add+1])
        check_DB2 = pd.DataFrame(columns = DB_col_list)
        check_DB2.loc[0] = sheet_checks.loc[i_check,DB_col_list]
        check_DB2['Label'] = pr
        check_DB2['servertime'] = [np.datetime64(a).astype(datetime) for a in check_DB2['servertime']]
        check_DB2['last_fail'] = [np.datetime64(a).astype(datetime) for a in check_DB2['last_fail']]                
        check_DB2[['deviceid',
              'dsc247','consecutiveFails']] = check_DB2[['deviceid','dsc247',
                                          'consecutiveFails']].apply(pd.to_numeric, errors='coerce')
                
        check_DB3 = pd.DataFrame(check_DB.iloc[ind_add+1:])
        check_DB = pd.concat([check_DB1, check_DB2, check_DB3],  ignore_index=True)        
        
    if (pr != 'ND'):
        #--------- update google sheet
        i_rmv = i_check

        if g_rmd == 0:
            sheet.delete_row(i_rmv+1)
            g_rmd = 1
                
        #--------- update local sheet
        if DB_rmd  == 0:
            sheet_checks = sheet_checks.drop(i_rmv).reset_index(drop = True)        
            DB_rmd = 1
        
        
        pickle.dump({'check_DB':check_DB}, open(load_file, 'wb'))
        continue
    
    i_check +=1
