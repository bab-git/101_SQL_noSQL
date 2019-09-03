# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 13:55:19 2019

The pipeline to extract data from mongoDB and saving in excell file
for further annotation.

A part is dedicated to data completion for case we need the trajectory of the fails on occation

@author: Babak Hosseini
"""
print(__doc__)

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

Mclient = MongoClient('mongodb://192.168.2.208:27018')

db = Mclient.sms
db.list_collection_names()

os.chdir('C:\\101_task')

clients = db['client']
checks = db['check']
#%%============
clients.count_documents({})
#%%============  read false sheet data
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("check-short-list").sheet1
#sheet = client.open("Checks comparison").sheet1
list_of_false = sheet.get_all_values()
false_SQL=pd.DataFrame(list_of_false)#, ascending = False)  
head_SQL = pd.Series(['name','H priority','threshold','wrong'])
#head_SQL = false_SQL.iloc[1]
false_SQL = false_SQL[1:]
false_SQL = false_SQL.rename(columns = head_SQL)
wrong_checks = false_SQL.loc[(false_SQL['wrong'] == 'TRUE') | (false_SQL['H priority'] == 'NA'),'name']
normal_checks = false_SQL.loc[false_SQL['H priority'] == 'FALSE','name']

def H_annot(checkname,extra):
    pr = 'ND'  #not determined
    #find wrong check
    wrong_find =list(filter(lambda i: checkname.find(i) >=0,wrong_checks))
    normal_find =list(filter(lambda i: checkname.find(i) >=0,normal_checks))
    if wrong_find:
        pr = 'ignore'    
    elif normal_find:
        pr = 'nH'
    elif checkname.find('Terra Backup') >= 0:
        pr = 'H'
#    elif checkname.find('Festplattenspeicherüberprüfung - Laufwerk') >= 0:
#        ind_F = extra.find('Frei:')
#        if ind_F >=0:
#            ext = extra[ind_F+5:]            
#            num = ext[:ext.find('GB')]
#            num=num.replace('.','')
#            num=num.replace(',','.')
#            if float(num) < 5:
#                pr = 'H'  # high P   
#            else:
#                pr = 'nH'  # high P   
    return pr
#%%================= test H_annot
#    H_annot()


#%%==================== List of active devices for the month
# getting list of device ids for WK ans servers
pipelin3 = [
        
           {
           "$lookup":
                     {
                       "from": "site",
                       "localField": "siteid",
                       "foreignField": "_id",
                       "as": "site"
                      }    
            },
            {
                "$unwind": {"path": "$site", "preserveNullAndEmptyArrays": True}
            },
            {
                 "$lookup": 
                    {
                        "from": "client",
                        "localField": "site.clientid",
                        "foreignField": "_id",
                        "as": "client"
                    }      
            },
            {
                "$unwind": {"path": "$client", "preserveNullAndEmptyArrays": True}
            },
            {"$match": {"site.enabled" : True}},
            {"$match": {"client.apiKey":"ae0a4c75230afae756fcfecd3d2838cf"}},
            {"$match": {"dscLocalDate": {"$gt":datetime(2019,7,1)}}},
#            {"$count": "device count"},
            {
                    "$project": {
                                    "device_name":"$name",
                                    "site_name":"$site.name",
                                    "client_name":"$client.name",
#                                    "name" : 1
                                }
            },            
         ] 
WK_list = list(db.workstation.aggregate(pipelin3))
SV_list = list(db.server.aggregate(pipelin3))
WK_db = pd.DataFrame(WK_list)
WK_db['Type'] = "workstation"
#WK_db = pd.DataFrame({values:WK_db.values, 'Type':'Workstation'}, index = index)
SV_db = pd.DataFrame(SV_list)
SV_db['Type'] = "server"
device_db = pd.concat([SV_db,WK_db], ignore_index = True)
device_db.head(2)
#%%==================== loop of getting faield checks - for the month
save_file = 'check_extraction.sav'
#loaded_data = pickle.load( open(save_file, "rb" ))
#i = loaded_data ['device_i']
#check_DB = loaded_data['check_DB']

i = 0
year_prob=[]
DB_col_list = ['device_name','Type','checkstatus',
                                    'description','servertime','last_fail',
                                    'client_name','site_name','extra',
                                    'dsc247','deviceid','checkid','consecutiveFails',
                                    'Label']
check_DB=pd.DataFrame(columns = DB_col_list)
#check_DB=pd.DataFrame(columns = DB_col_list+['Label'])
excel_path = 'check_list.xlsx'
if os.path.isfile(excel_path):
    os.remove(excel_path)

# %%===========   loop over the devices
while i < len(device_db):
#while i <= len(device_db):shab mi
#    i = 0
    #device_id = WK_list[i]['_id']    
    #  %%
    device_id = int(device_db['_id'][i])
    print('\nGetting checks for device_id:',i,'/',len(device_db),'(%s)' % (device_db['device_name'][i]),'...')
#    device_id=int(device_db['_id'][device_db['device_name']=='SRV-PR-01'])
#    device_id = 1054972
#    del resultsd
    results = checks.find(
                {
                    "servertime":
                    {
                                    "$gte": datetime(2019,6,1,0,0,0),
                                    "$lte": datetime(2019,7,31,23,59,59)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":1054972,
    #                "dsc247":2, 
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "26706789"
                }
                ,projection={'datetime': False}
                )
#    try:
    check_results = list(results)
#    except pymongo.errors.InvalidBSON:
#       print('year format prblem ==> skip the device')
#       i+=1
#       year_prob.append(device_id)
#       break
    #  %%
    len_fails = len(check_results)
    print('number of failed checks:',len_fails)
#  %%
    if len(check_results) == 0:
        i+=1
        continue
    print('Prepaing the SQL table...')
    check_SQL=pd.DataFrame(check_results, columns = ['servertime','description',
                                                     'checkstatus','consecutiveFails','dsc247',
                                                     'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                    ['checkid','servertime'])#, ascending = False)                              
    temp = device_db.loc[i,['device_name','client_name','site_name','Type']]
    check_SQL[['device_name','client_name','site_name','Type']] = check_SQL.apply(lambda row: temp, axis = 1)      
    check_SQL = check_SQL.reset_index(drop = True)
    check_SQL['consFails'] = ''
    check_SQL['last_fail'] = ''
    check_SQL0 = check_SQL.copy()  # for debuging - todo remove
    
    check_current = check_SQL.loc[0,'checkid']
    check_SQL.loc[0,'consFails'] = check_SQL.loc[0,'consecutiveFails']
    check_SQL.loc[0,'last_fail'] = check_SQL.loc[0,'servertime']
    dsc247 = check_SQL['dsc247'][0]
   
    i_f = 1
 #  %%   loop over the check-fail rows
    while i_f < len(check_SQL):
#            if check_SQL['servertime'][i_f] >= datetime(2019,6,3,7,10,0):
#                break   
#  %%                 
        check_next = check_SQL.loc[i_f,'checkid']
#        if check_next == '26706789':
#            break        
        checkname = check_SQL.loc[i_f,'description']
        extra = check_SQL.loc[i_f,'extra']
        if H_annot(checkname,extra)=='ignore': # check-definite label 3 case
            check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
            #                print('ignore')
#            print('continue')
            continue
                
        if check_next == check_current:  # same check
            seq = 0  # flags the existing sequence

            a = check_SQL['last_fail'][i_f-1]
            b = check_SQL['servertime'][i_f]
            cons_b = check_SQL['consecutiveFails'][i_f]
            cons_a = check_SQL['consecutiveFails'][i_f-1]
            
            if ((b - a).total_seconds() < 3.5*3600): # 2-3hr consequative errors
                seq = 1
            elif (b.day-a.day == 1 or (b.day-a.day <0 and (b-a).total_seconds() < 24*3600) ): # next day sequence
                if dsc247 == 2 : # safety check or consecutiveFails
                    seq = 1
                else:    # look for in between testok!
                    
                    results = checks.find(
                                        {
                                            "servertime": {
                                                            "$gte": a,
                                                            "$lte": b
                                                            },    
                                            "deviceid":device_id,                                
                                            "checkstatus": "testok",
                                            "checkid": check_current                                            }
                                        )
                    temp_results = list(results)
                    if len(temp_results) == 0: # continues fail sequence
                        seq = 1
            if seq == 1:  # continues failing sequanece ==> clear it from the table    
                check_SQL.loc[i_f-1,'extra'] = check_SQL.loc[i_f,'extra']
                check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
                i_f -= 1
                
            check_SQL.loc[i_f,'last_fail'] = b
            check_SQL.loc[i_f,'consFails'] = cons_b
        else:  # new check            
            # adding new row
#                break
#                print('break')
            dsc247 = check_SQL['dsc247'][i_f]
            check_SQL.loc[i_f,'last_fail'] = check_SQL.loc[i_f,'servertime']
        
        if (check_next != check_current) | (seq == 0):
            # categorizing previous row#                
            checkname = check_SQL.loc[i_f-1,'description']
            extra = check_SQL.loc[i_f-1,'extra']
            pr = H_annot(checkname,extra)
            if pr == 'ignore':
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
#                    print('ignore')
            elif (pr=='nH')|(pr=='H'): # check-definite label H/N case
#                    break
                temp = check_SQL.loc[i_f-1,DB_col_list[:len(DB_col_list)-1]]
                temp['consecutiveFails'] = check_SQL.loc[i_f-1,'consFails']
                temp['Label'] = pr
                check_DB= check_DB.append(temp,ignore_index=True)
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
#                    print('Add')                    
#                    break                                        
                
        if check_SQL['consFails'][i_f]=='':
                check_SQL.loc[i_f,'consFails'] = check_SQL.loc[i_f,'consecutiveFails']
        check_current = check_next                
        i_f += 1
#  %%
    # Annotate last entry of SQL table  
    pr = H_annot(checkname,extra)
    if pr == 'ignore': # check-definite label 3 case
        check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
    elif (pr=='nH')|(pr=='H'): # check-definite label H/N case
        temp = check_SQL.loc[i_f-1,DB_col_list[:len(DB_col_list)-1]]
        temp['consecutiveFails'] = check_SQL.loc[i_f-1,'consFails']
        temp['Label'] = pr
        check_DB= check_DB.append(temp,ignore_index=True)     
        check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
    #  %%        
            
    check_SQL_last = check_SQL[['device_name','Type','checkstatus',
                                'description','servertime','last_fail',
                                'client_name','site_name','extra',
                                'dsc247','deviceid','checkid','consFails']]
    check_SQL_last = check_SQL_last.rename(columns = {"consFails":"consecutiveFails"})
    check_SQL_last = check_SQL_last.sort_values(by = 'servertime')
    
    #----------- save python data
    save_file = 'check_extraction.sav'
    pickle.dump({'device_i':i,'check_DB':check_DB}, open(save_file, 'wb'))
    
    #----------- save to files
    if len(check_SQL_last) == 0:
        print('0 checks remained to save to the excel file...')
        i += 1
        continue
    
    print('Saving', len(check_SQL_last), 'extracted failes to the excel file...')        
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
          =============================
          """
          )
    i += 1    
#    loaded_data = pickle.load( open(filename, "rb" ))
    
#%%==================== Check the running operations
#break    
a=db.current_op()
print(len(a['inprog'])-1,'operation is still running')
#if len(a['inprog']) > 1:
#    print("Still running operations")
#else:
#    print("All is good!")
        
#agg_expl = db.command('aggregate','check',pipeline=pipeline, explain=True)

#            {"$group": {"_id":"$deviceid", "max_time":{"$max":"$servertime"}}}    


#print(client.f)

#connection = Connection()
#connection = Connection()
#%%==================== Check specific cases
results = checks.find(
                {
                    "servertime": {
                                    "$gte": datetime(2019,6,1,0,0,1),
                                    "$lte": datetime(2019,7,31,23,59,59),
#                                    "$ne": "false"
                                    },    
#                    "servertime": datetime(2019,3,1,18,51,21),
                    "deviceid":1054972,
    #                "dsc247":2,
#                    "checkstatus": {"$ne":"testok"},            
                    "checkid": "26706789"
                }
                ,projection={'datetime': False}
                )
some_results = list(results)
partial_SQL=pd.DataFrame(some_results, columns = ['servertime','description',
                                                         'checkstatus','consecutiveFails','dsc247',
                                                         'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                        ['checkid','servertime'])#, ascending = False)    

partial_SQL.head(2)
#ISODate("2019-03-01T16:39:48.000Z") 1141533
#2019-03-01 18:09:40.000Z 745934
#2019-03-01 16:39:48.000Z
# %% performance test
del results
start = time.time()
results = checks.find(
                {
                    "servertime": {
                                    "$gte": datetime(2018,2,1,0,0,0),
                                    "$lte": datetime(2018,12,1,1,0,0,0)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":745976,
    #                "dsc247":2,
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "16880587"
                }
                )
some_results = list(results)
end = time.time()
print(end - start)

del results
start = time.time()
for i_t in range(0,5):
#    print(i_t)
    results = checks.find(
                {
                    "servertime": {
                                    "$gte": datetime(2018,2+i_t*2,1,0,0,0),
                                    "$lte": datetime(2018,2+(i_t+1)*2,1,1,0,0,0)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":745976,
    #                "dsc247":2,
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "16880587"
                }
                )
    some_results = list(results)
end = time.time()
print(end - start)

del results
start = time.time()
for i_t in range(0,10):
#    print(i_t)
    results = checks.find(
                {
                    "servertime": {
                                    "$gte": datetime(2018,2+i_t,1,0,0,0),
                                    "$lte": datetime(2018,2+i_t+1,1,1,0,0,0)
                                    },    
                    "deviceid":device_id,
#                    "deviceid":745976,
    #                "dsc247":2,
                    "checkstatus": {"$ne":"testok"},
#                    "checkid": "16880587"
                }
                )
    some_results = list(results)
end = time.time()
print(end - start)

#%%=======================    test commands
pprint.pprint(clients.find_one(
        {
#                servertime: {"$gt": new ISODate("2019-07-26 01:00:55.000Z")}
            "name":"101 - Busold Consulting"
        }))
#%==============================================
result = checks.find_one(
        {
#                servertime: {"$gt": new ISODate("2019-07-26 01:00:55.000Z")}
            "deviceid":1156225
        })

pprint.pprint(result)
#%===================================
results = checks.find(
        {
            "deviceid":1156225
        }
        ).limit(2)

for result in results:
    pprint.pprint(result)
    #%%============ find last entry
pipeline = [ 
            {"$match":{
                        "$and":[
                                  {"servertime":
                                      {"$gte": datetime(2019,7,31),"$lt": datetime(2019,8,1)}},
                                  {"deviceid":1035046}
                                ]
                     }},            

            {"$group":
                {
                  "_id":"$deviceid",    
                  "max_time":{"$max":"$servertime"},
#                  "count": {"$sum":1},
                }}
            #{"$limit":1},                                                                     
           ]

#{"deviceid":1035046}
#{"$gte": 'new ISODate("2019-07-31 00:00:08.000Z")'}},
agg_result = list(db.check.aggregate(pipeline))[0]
pprint.pprint(agg_result)
T_end = agg_result['max_time']
#%%==================== last-1 entry
pipeline2 = [ 
            {"$match":{
                        "$and":[
                                  {"servertime":
                                      {"$gte": datetime(2019,7,31),"$lt": T_end}},
                                  {"deviceid":1035046}
                                ]
                     }},            

            {"$group":
                {
                  "_id":"$deviceid",    
                  "max_time":{"$max":"$servertime"},
#                  "count": {"$sum":1},
                }}
            #{"$limit":1},                                                                     
           ]
agg_result = list(db.check.aggregate(pipeline2))[0]
T_end_1 = agg_result['max_time']
Ts=T_end.hour-T_end_1.hour   # sampling time