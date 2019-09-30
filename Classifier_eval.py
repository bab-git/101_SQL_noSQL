# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:43:27 2019

Two types of evaluations for the designed classifier:
    A: extracting mongoDB data to a google sheet while classifiying its rows
    B: classifiying the already extracted data of a google sheet and comparing 
       to a given grand truth

trained_classifier: the file which contains the trained classifier

Coded_classes: contains the table of decision trees design for different types of check
               , the relevant feature encodings, and the direct decision making rules.

level:  a variable to decide if the classification task is binary or 3-class
    
@author: Babak Hosseini
"""

print(__doc__)
#from mongo_classifier import H_annot, class_code
import numpy as np
import pandas as pd
import os
from openpyxl import load_workbook
#from sklearn.base
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics
from matplotlib import pyplot as plt
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.datasets import make_classification, make_moons, make_circles
from matplotlib.colors import ListedColormap
from sklearn.svm import SVC
from sklearn import tree   
from git import Repo
from pymongo import MongoClient

import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials 

from git import Repo
from gspread_pandas import Spread

Mclient = MongoClient('mongodb://192.168.2.208:27018')

db = Mclient.sms
db.list_collection_names()

os.chdir('C:\\SYNX')

clients = db['client']
checks = db['check']
#%%==================== List of active devices for the month
# getting list of device_ids for work station and servers with specific api key!
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
#            {"$match": {"dscLocalDate": {"$gt":datetime(2019,7,1)}}},
#            {"$count": "device count"},
            {
                    "$project": {
                                    "device_name":"$name",
                                    "site_name":"$site.name",
                                    "client_name":"$client.name",
#                                    "dscLocalDate":"$dscLocalDate"
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

#%%===========================================================================
#==================== A: Extracting data rows from mongoDB and classify the evaluation set
#===========================================================================    
#------ safety measure
modif_code = 'green'  # Enter this code if you really want to modify the spreadsheet
get_code = input('''
You are about to delete the "google spread sheet"
and rebuild them from scrath!! 
--------------------
You can also rename the target sheet and save file by "g_sheet_name"
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
      to get the google sheet before modification...''')


#------------------
import mongo_classifier # this step is necessary to update the classifier data

load_file = 'trained_classifier.sav'
loaded_classifier = pickle.load( open(load_file, "rb" ))

level = 1 # 1: H/nH   2: H/ N/ F
eval_sheet = "Check evaluation_test"


head_ind = 8

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Checks list").sheet1

sheet_g = Spread(eval_sheet)
sheet_g.open_sheet("Sheet1", create=False)   
sheet_g.sheet.resize(rows=head_ind)

headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
check_SQL  = pd.DataFrame(all_values, columns = headers) 

all_checks = list(check_SQL.loc[range(head_ind,len(check_SQL)),'description'].unique())


#====== validation loop

DB_col_list = ['device_name','Type','checkstatus',
                                    'description','servertime','last_fail',
                                    'client_name','site_name','extra',
                                    'dsc247','deviceid','checkid','consecutiveFails',
                                    'Label']
i_dev = 0
#  %%
while i_dev < len(device_db):
    device_id = int(device_db['_id'][i_dev])
    print('\nGetting checks for device_id:',i_dev,'/',len(device_db),'(%s)' % (device_db['device_name'][i_dev]),'...') 
    results = checks.find(
                {
                    "servertime":
                    {
                                    "$gte": datetime(2019,8,1,0,0,0),
                                    "$lte": datetime(2019,8,31,23,59,59)
                                    },    
                    "deviceid":device_id,
                    "checkstatus": {"$ne":"testok"},
                }
                ,projection={'datetime': False}
                )
    check_results = list(results)
    
    len_fails = len(check_results)
    print('number of failed checks:',len_fails)
    if len(check_results) == 0:
        i_dev+=1
        continue
    print('Prepaing the SQL table...')
    check_SQL=pd.DataFrame(check_results, columns = ['servertime','description',
                                                     'checkstatus','consecutiveFails','dsc247',
                                                     'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                    ['checkid','servertime'])#, ascending = False)     
   
    temp = device_db.loc[i_dev,['device_name','client_name','site_name','Type']]
    check_SQL[['device_name','client_name','site_name','Type']] = check_SQL.apply(lambda row: temp, axis = 1)      
    check_SQL = check_SQL.reset_index(drop = True)
    check_SQL['consFails'] = ''
    check_SQL['last_fail'] = ''
    check_SQL['Label'] = ''
    check_SQL0 = check_SQL.copy()  # for debuging - todo remove

    check_current = check_SQL.loc[0,'checkid']
    check_SQL.loc[0,'consFails'] = check_SQL.loc[0,'consecutiveFails']
    check_SQL.loc[0,'last_fail'] = check_SQL.loc[0,'servertime']
    dsc247 = check_SQL['dsc247'][0]
   
    i_f = 1    
 #  %%   loop over the check-fail rows
    while i_f < len(check_SQL):        
        SQL_row = check_SQL.iloc[i_f].copy()
        check_next = check_SQL.loc[i_f,'checkid']
        checkname = check_SQL.loc[i_f,'description']
        extra = check_SQL.loc[i_f,'extra']
        seq = 0
        pr = mongo_classifier.label_pred(SQL_row,loaded_classifier,level)        
        if pr in {'ignore','nH'}: # check-definite label 1,3 case            
            check_SQL = check_SQL.drop(i_f).reset_index(drop = True)            
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
            dsc247 = check_SQL['dsc247'][i_f]
            check_SQL.loc[i_f,'last_fail'] = check_SQL.loc[i_f,'servertime']
        
        if (check_next != check_current) | (seq == 0):
            # categorizing previous row#                
            checkname = check_SQL.loc[i_f-1,'description']
            extra = check_SQL.loc[i_f-1,'extra']
            
            SQL_row = check_SQL.loc[i_f-1].copy()
            pr = mongo_classifier.label_pred(SQL_row,loaded_classifier,level)
            if pr in {'ignore','nH'}: # check-definite label 1,3 case
                check_SQL = check_SQL.drop(i_f-1).reset_index(drop = True)
                i_f -= 1
            else: # Nan or ND or H
#                raise ValueError('end i_f')                        
                check_SQL.loc[i_f-1,'Label'] = pr
                
        if check_SQL['consFails'][i_f]=='':
                check_SQL.loc[i_f,'consFails'] = check_SQL.loc[i_f,'consecutiveFails']
        check_current = check_next                
        i_f += 1
#  %%
    # -------Annotate last entry of SQL table
    i_f = len(check_SQL)-1
    checkname = check_SQL.loc[i_f,'description']
    extra = check_SQL.loc[i_f,'extra']    
    
    SQL_row = check_SQL.iloc[i_f].copy()
    if pr in {'ignore','nH'}: # check-definite label 1,3 case
        check_SQL = check_SQL.drop(i_f).reset_index(drop = True)
    else: # Nan or ND or H
#        raise ValueError('end i_f')                        
        check_SQL.loc[i_f,'Label'] = pr
            
    check_SQL_last = check_SQL[['device_name','Type','checkstatus',
                                'description','servertime','last_fail',
                                'client_name','site_name','extra',
                                'dsc247','deviceid','checkid','consFails','Label']]
    check_SQL_last = check_SQL_last.rename(columns = {"consFails":"consecutiveFails"})
    check_SQL_last = check_SQL_last.sort_values(by = 'servertime')
    
    
    #----------- save to server
    if len(check_SQL_last) == 0:
        print('0 checks remained to save to the excel file...')
        i_dev += 1
        continue
    
#    raise ValueError('to save')
    print('Saving', len(check_SQL_last), 'extracted failes to the google sheet...')        
    sheet_g = Spread(eval_sheet)
    sheet_g.open_sheet("Sheet1", create=False)    
    
    last_row = sheet_g.sheet.row_count        
    sheet_g.df_to_sheet(check_SQL_last, index=False, headers = False,sheet='Sheet1', 
                        start=(last_row+2,1),  replace = False)
    
    print("""
          =========== table saved in google sheet =====
          =============================
          """
          )
    i_dev += 1  
    
#%%===========================================================================
#% ============== B: Label prediction for data of google sheet 
#% ===========================================================================
load_file = 'trained_classifier.sav'
loaded_classifier = pickle.load( open(load_file, "rb" ))


head_ind = 8        # index of the header
label_col = 15

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Check evaluation").sheet1

check_list = sheet.col_values(11)
valid_rows = list(filter(lambda x: check_list[x] != '', range(head_ind,len(check_list))))
valid_rows = [int(x) for x in valid_rows]

#fails_select = sheet.row_values(8)
headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
SQL_test  = pd.DataFrame([all_values[i] for i in valid_rows] , columns = headers)
SQL_test0 =  SQL_test.copy()
SQL_test['pred Label'] = ''

# ====== classificartion loop
i_row = 0
level = 1  # 1: H/nH   2: H/ N/ F
SQL_miss= pd.DataFrame(columns = headers)
while i_row < len(SQL_test):
    SQL_row = SQL_test.iloc[i_row].copy()
#    SQL_row0 = SQL_row.copy()
    pr = mongo_classifier.label_pred(SQL_row,loaded_classifier,level)
    SQL_test.loc[i_row,'pred Label'] = pr
    if pr== 'H' and SQL_row['real label']!='2':
#        raise ValueError
        SQL_miss = SQL_miss.append(SQL_test.iloc[i_row],ignore_index=True)
    i_row += 1
        
print ('all rows are analyzed')            


#----- conf-matrix of the result
#pred_label = np.array(SQL_test_l2['pred Label'])
pred_label = np.array(SQL_test['pred Label'])
true_label = np.array(SQL_test['real label'])

# finding Ned and New cases in the result
ind_Ned = np.where(pred_label=='Ned')
ind_New = np.where(pred_label=='new')
ind_remove = np.concatenate((ind_Ned,ind_New),axis = 1)

# Treating all Ned and New cases as Noraml failures
pred_label[ind_remove]=1

# Excluding all 5 cases from the analysis (failure which were not annotated)
ind_5 = np.where(true_label=='5')
pred_label = np.delete(pred_label,ind_5)
true_label = np.delete(true_label,ind_5)

if level ==1:    
    # Treating all ignore cases as normal failures for binary classification
    ind_3 = np.where(true_label=='3')
    true_label[ind_3]='1'

# Excluding all 4 cases from the analysis (failure which are skipped for later time)
ind_4 = np.where(true_label=='4')
pred_label = np.delete(pred_label,ind_4)
true_label = np.delete(true_label,ind_4)

true_label = [int(x) for x in true_label]
if isinstance(pred_label[0],str):
    pred_label = [label_dic[x] for x in pred_label]
else:
    pred_label = [int(x) for x in pred_label]

metrics.confusion_matrix(true_label,pred_label, labels = np.unique(true_label))