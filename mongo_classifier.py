# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:43:27 2019

The classifier which is designed to categorize the priority of a given check result from mongoDB

@author: Babak Hosseini
"""


# %% ================= the coded annotation rules based on the google sheet "check-short-list"
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#from gspread_pandas import Spread
import pandas as pd

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("check-short-list").sheet1
list_of_false = sheet.get_all_values()
false_SQL=pd.DataFrame(list_of_false)#, ascending = False)  
head_SQL = pd.Series(['name','H priority','thresh_type','thresh','extra'])

false_SQL = false_SQL[1:]
false_SQL = false_SQL.rename(columns = head_SQL)
wrong_checks = false_SQL.loc[(false_SQL['H priority'] == 'NA'),'name']
#wrong_checks = false_SQL.loc[(false_SQL['wrong'] == 'TRUE') | (false_SQL['H priority'] == 'NA'),'name']
normal_checks = false_SQL.loc[false_SQL['H priority'] == 'FALSE','name']
thresh_checks = false_SQL.loc[(false_SQL['thresh_type'] != ''),'name']
extra_checks = false_SQL.loc[(false_SQL['extra'] != ''),'name']
High_checks = false_SQL.loc[(false_SQL['H priority'] == 'TRUE') & 
                            (false_SQL['thresh_type'] == '') & (false_SQL['extra'] == ''),'name']

def H_annot(checkname,extra):
    pr = 'ND'  #not determined
    #find wrong check
    wrong_find =list(filter(lambda i: checkname.find(i) >=0,wrong_checks))
    normal_find =list(filter(lambda i: checkname.find(i) >=0,normal_checks))
    thresh_find =list(filter(lambda i: checkname.find(i) >=0,thresh_checks))
    extra_find =list(filter(lambda i: checkname.find(i) >=0,extra_checks))
    high_find =list(filter(lambda i: checkname.find(i) >=0,High_checks))    
    
    if wrong_find:
        pr = 'ignore'    
    elif normal_find:
        pr = 'nH'
    elif high_find:
        pr = 'H'
    elif extra_find:
        if checkname.find('Sicherungsüberprüfung') >= 0:
            if extra in {'Fehler bei einer oder mehreren Aufgaben',
                         'Nicht ausreichend Aufgaben gefunden'}:
                pr = 'H'
            elif extra in {'Produkt nicht gefunden','Produkt nicht gefunden'
                           ,'Keine Backupinformationen gefunden','Backupstatus kann nicht abgerufen werden',
                           ""}:
                pr = 'Nan'
        
    elif thresh_find:
        ind_1 = extra.find('t:')
        if ind_1 >=0:
            tot_size = extra[ind_1+2:extra.find('GB')]
            tot_size=float(tot_size.replace('.','').replace(',','.'))
           
#            ind_F = 
            ext = extra[extra.find('Frei:')+5:]
            free_size = ext[:ext.find('GB')]
            free_size=float(free_size.replace('.','').replace(',','.'))
                        
            if free_size/tot_size < .2:  # 20% free threshold
                pr = 'H'  # high P   
            else:
                pr = 'nH'  # high P                   

    return pr

# %% ================= Some coded classification rules
#!!!! already coded in the feature selection part
def class_code(row_SQL):
    pr = 'ND'  #not determined
    
    #PING-Überprüfung
    if row_SQL['description'].find('PING-Überprüfung')>=0:
        if row_SQL['deviceid'] in {590715,801799,1090258}:
            pr = 'H'
        elif row_SQL['deviceid'] in {754547,620692}:
            pr = 'nH'
    elif row_SQL['description'].find('Ereignisprotokollüberprüfung')>=0 & row_SQL['description'].find('Backup')>=0:
        if row_SQL['extra'] == 'Ereignis nicht gefunden':
            pr = 'H'
        elif row_SQL['extra'].find('successfully')>=0:
            pr = 'ignore'        
            
            
    return pr

#%% ===================== check desctiption splitter
def des_split(description,key):
    if len(description)>len(key):
        shortened = description[len(key):]
    else:
        shortened = ''
    return shortened



#%% ===================== encoding trained classifiers
class encoded_class:
    def __init__(self):
        self.feat_name = ''
        self.split_name = ''
        self.classifier = ''
        self.label = ''
#%% ===================== Label prediction function
#head_ind = 8

#scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
#client = gspread.authorize(creds)
#sheet = client.open("Checks list").sheet1

#headers = sheet.row_values(head_ind)
#all_values = sheet.get_all_values()
#check_SQL  = pd.DataFrame(all_values, columns = headers) 
#all_checks = check_SQL.loc[range(head_ind,len(check_SQL)),'description'].unique()
    
def label_pred(SQL_row,loaded_classifier,level):
    # level: 1= H/nH/Nan   2= 1/2/3/Nan
    coded_classes = loaded_classifier['coded_classes']
    server_dic = loaded_classifier['server_dic']
    
    checkname = SQL_row['description']
    extra = SQL_row['extra']
    
    pr = H_annot(checkname,extra)
#    pr2 = class_code(SQL_row)
    
    if pr == 'ND': # check was not a definite case                  
#        all_checks = coded_classes['split_name']
        chk_found = list(filter(lambda i: coded_classes.loc[i,'split_name'] in checkname,range(len(coded_classes))))
        if chk_found ==[]:
            pr = 'new'
        else:  # data was seen in trainig
            chk_found = chk_found[0]
            clf_data = coded_classes.iloc[chk_found]
            if clf_data['classifier'] == '' and clf_data['score'] == 1:
#                raise ValueError('solo class')
                pr = int(clf_data['label'])
            elif clf_data['classifier'] == '' and clf_data['score'] == 0:
#                raise ValueError('Nan data- no trainig enough')
                pr = 'Nan'
            elif checkname in clf_data['detail']['des_solo'] or extra not in clf_data['detail']['ex_list']:
#                raise ValueError('Nan data - not trained')
                pr = 'Nan'
            else: # using the trained classifier
                                
                SQL_row['Type'] = server_dic[SQL_row['Type']]
                SQL_row[['deviceid','dsc247',
                               'consecutiveFails']] = SQL_row[['deviceid','dsc247',
                                                  'consecutiveFails']].apply(pd.to_numeric, errors='coerce')
    
    
                key = clf_data['split_name']
                sub_list = clf_data['detail']['sub_list']
                SQL_row['sub_description'] = des_split(SQL_row['description'],key)
                if SQL_row['sub_description'] not in sub_list:
                    pr = 'Nan'                    
                else:                    
                    SQL_row['sub_desc_qnt'] = sub_list[SQL_row['sub_description']]             
                    
                    ex_list = clf_data['detail']['ex_list']
                    SQL_row['extra_qnt'] = ex_list[SQL_row['extra']]
                                    
                    feat_names = clf_data['feat_names'] 
                    x = SQL_row[feat_names[:len(feat_names)-1]].to_numpy()                
                    clf = clf_data['classifier']
                    pr = clf.predict(x.reshape(1,-1))
                    pr = int(pr[0])
    
    #convert the level
    conv_lv1 = {2:'H',1:'nH',3:'nH'}
    conv_lv2 = {'H':2,'nH':1,'ignore':3}
    conv_str = {'Nan':'Ned','ND':'Ned','new':'new'}
    if isinstance(pr, str) and (pr in {'Nan','ND','new'}): #is string    
        pr = conv_str[pr]
    elif level==1 and isinstance(pr, int):
            pr = conv_lv1[pr]
    elif level==2 and isinstance(pr, str):
            pr = conv_lv2[pr]
            
    if level==1 and pr =='Ned':
        pr = 'nH'
        
    return pr