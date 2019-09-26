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

# %% ================= The coded classification rules
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