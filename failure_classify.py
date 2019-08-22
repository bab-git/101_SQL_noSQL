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
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics



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
#fails = fails.drop(fails[fails['device_name']==''].index).reset_index(drop = True)

# %% quantifying the features
#fails.drop(['description', 'servertime', 'device_name'])
fails_select = pd.DataFrame(fails, columns = ['checkstatus','consecutiveFails','dsc247',
                                              'checkid','deviceid','Label','servertime',
                                              'extra'])

# convert strings to numbers
check_dic = {'testok':1, 'testerror':2, 'testalertdelayed':3,'testcleared':4,'test_inactive':5, 'testok_inactive':6,'testerror_inactive':7}
fails_select['checkstatus']=list(map(lambda x:check_dic[x],fails_select['checkstatus']))

#fails_select['servertime'] = list(map(lambda x: np.datetime64(x).astype(datetime),fails_select['servertime']))
time_index = list(map(lambda x: np.datetime64(x).astype(datetime),fails_select['servertime']))
fails_select[['deviceid','checkid',
              'dsc247','consecutiveFails','Label']] = fails_select[['deviceid','checkid',
                                          'dsc247','consecutiveFails','Label']].apply(pd.to_numeric, errors='coerce')
# %% to numpy
fails_mat = fails_select[['checkstatus','consecutiveFails','dsc247',
                                              'checkid','Label']].to_numpy()
#np.c_[fails_mat,np.array(fails_select['servertime'])]
X = fails_mat[:,0:4]
y = fails_mat[:,4]
datasets = (X,y)
X=StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test = \
        train_test_split(X,y,test_size = .2, random_state = 42)
classifier_DT = DecisionTreeClassifier(max_depth = 5)
classifier_RF = RandomForestClassifier(max_depth = 5, n_estimators= 20, max_features = 1)

classifier_DT.fit(X_train,y_train)
scode_DT = classifier_DT.score(X_test,y_test)
print('Decision tree score:',scode_DT)

classifier_RF.fit(X_train,y_train)
scode_RF = classifier_RF.score(X_test,y_test)
print('Random Forest score:',scode_RF)

y_pred_DT = classifier_DT.predict(X_test)
y_pred_RF = classifier_RF.predict(X_test)

print("Labels:", np.unique(y_test))
print(metrics.confusion_matrix(y_test,y_pred_DT, labels = np.unique(y_test)))
metrics.confusion_matrix(y_test,y_pred_RF, labels = np.unique(y_test))