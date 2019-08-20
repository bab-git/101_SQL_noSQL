# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:43:27 2019

Analysis of the annotated data from mongoDB containing fail checks

@author: Babak Hosseini
"""

print(__doc__)
import numpy as np
import pandas as pd
import os
from openpyxl import load_workbook




# %% importing annotated data from excell file
excel_path = 'Checks list - update_ 19.08.xlsx'
print('Reading data from the excel sheet...')        
try:
    os.path.isfile(excel_path)
except:
    print("file not found")
    
book = load_workbook(excel_path)
last_row = book['Sheet1'].max_row
print("%d rows in the excel file" % last_row)
fails = pd.read_excel(excel_path, header = 7)
fails.fillna('', inplace=True)
fails['excel_ind'] = fails.index
fails = fails.drop(fails[fails['Label']==''].index).reset_index(drop = True)

# %% quantifying the features
#fails.drop(['description', 'servertime', 'device_name'])
fails_select = pd.DataFrame(fails, columns = ['checkstatus','consecutiveFails','dsc247',
                                              'checkid','deviceid','Label','servertime',
                                              'extra'])
