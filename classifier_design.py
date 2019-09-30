# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 16:43:27 2019

Analyzing of the annotated data of mongoDB (stored in google sheets) which contain failed-checks
to train or hand-design check classifiers

The hand-coded rules are stored in mongo_classifier.py module and are extracted from the online google sheet

Coded_classes: contains the table of decision trees design for different types of check
               , the relevant feature encodings, and the direct decision making rules.

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


import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials 

os.chdir('C:\\SYNX')


#%%===========================================================================
#==================== Feature extraction pipeline for XXX-YYY patterns
#===========================================================================    
# %%  safety check!
modif_code = 'green'  # Enter this code if you really want to modify the spreadsheet
get_code = input('''
You are about to modify the existing trained classifiers
in "trained_classifier.sav" file!! 
--------------------
You can also rename the target file by "save_file" 
if you want to work on a different data set
--------------------
If you know what you are doing, please enter the pass-code! ;-)
Pass-code:''')
if get_code != modif_code:
#    print('dsadsa')
    raise ValueError('''Wrong code! 
                Cannot continue!!''')

print('''If anything goes wrong, please check the git history 
      to get trained_classifie.sav before modification...''')

save_file = 'trained_classifier.sav'
import mongo_classifier

#-----git push
if os.path.isfile(save_file):
    repo = Repo(os.getcwd())
    repo.index.add([save_file])
    repo.index.commit("backup of check_DB before modification")
    origin = repo.remotes.origin
    origin.push()


head_ind = 8

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Checks list").sheet1  # where the labeld training data is stored
headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
fails  = pd.DataFrame(all_values, columns = headers) 
check_drp = (fails['checkstatus']=='')|(fails['checkstatus']=='add')|(fails['Label']=='4')|(fails['Label']=='5')|(fails['Label']=='')
fails = fails.drop(fails[check_drp].index).reset_index(drop = True)
fails = fails.drop(0).reset_index(drop = True)
all_checks = list(fails.loc[range(head_ind,len(fails)),'description'].unique())


# selecting features to use for the model
feat_names = ['sub_desc_qnt','extra_qnt','Type','Label']
#feat_names = ['sub_desc_qnt','extra_qnt','deviceid','Type','Label']
#feat_names = ['sub_desc_qnt','extra_qnt','deviceid','consecutiveFails','Label']

col = ['description','extra','deviceid','Type','servertime','last_fail',
                                    'dsc247','consecutiveFails',
                                    'checkstatus', 'Label']
    
label_dic = {'H':2,'nH':1,'1':1,'2':2,'3':3,'5':5,'Nan':5,1:1,2:2,3:3,4:4,5:5}
server_dic = {'server':1,'workstation':2}
    

class_cols = ['feat_name','split_name','classifier','label','score','feat_names','detail']
coded_classes = pd.DataFrame(columns = class_cols)

split_cand = []
group_feat = []

   
#  %% --------- extraction     
i_name = 0
while i_name < len(all_checks):
    feat = all_checks[i_name]
    split = 0
    if feat.find(' - ')>=0:
        split_cand.append(feat)
        name = feat[:feat.find(' - ')]
#        split = 1
        if name not in group_feat:
            group_feat.append(name)
        else:
#            raise ValueError('name in the group')
            i_name += 1
            continue
    else:
        name = feat    

    # data preprations
    ind1 = np.where([name in str for str in fails['description']])[0]
    temp_SQL = fails.loc[ind1]
    
#    ind2 = np.where([name in str for str in check_DB['description']])[0]
#    temp_DB= check_DB.loc[ind2]        
    
    check_SQL1 = temp_SQL[col]
#    check_SQL2 = temp_DB[col]
#    check_SQL=pd.concat([check_SQL1,check_SQL2]).reset_index(drop = True)
    check_SQL = check_SQL1.copy()
    
    check_SQL['Label'] = [label_dic[a] for a in check_SQL['Label']]
    check_SQL['Type'] = [server_dic[i] for i in check_SQL['Type']]
    check_SQL[['deviceid','dsc247',
               'consecutiveFails']] = check_SQL[['deviceid','dsc247',
                                  'consecutiveFails']].apply(pd.to_numeric, errors='coerce')
    
    check_drp = (check_SQL['checkstatus']=='add')|(check_SQL['Label']>=4)
    check_SQL = check_SQL.drop(check_SQL[check_drp].index).reset_index(drop = True)
    
    # description extraction
    key = name
    
    check_SQL['sub_description'] = [mongo_classifier.des_split(x,key) for x in check_SQL['description']]
    sub_names = check_SQL.sub_description.unique()
    sub_list = {}
    for value in range(0,len(sub_names)):
        sub_list[sub_names[value]] = value+1
    #fails_select = fails_select.drop('checkid', axis = 1)
    check_SQL['sub_desc_qnt'] = [sub_list[i] for i in check_SQL['sub_description']]
        
    extra_names = check_SQL.extra.unique()
    ex_list = {}
    for value in range(0,len(extra_names)):
        ex_list[extra_names[value]] = value+1
    #fails_select = fails_select.drop('checkid', axis = 1)
    check_SQL['extra_qnt'] = [ex_list[i] for i in check_SQL['extra']]
    
    df = pd.DataFrame(check_SQL,columns=['description'])
    df = df.drop_duplicates()
    # eliminate single samples
    df2 = check_SQL.groupby(['description']).size()
    des_solo = list(df2.loc[df2==1].index)
    
    solo_ind = list(filter(lambda x:check_SQL.loc[x,'description'] in des_solo, range(len(check_SQL))))
        
    check_SQL = check_SQL.drop(solo_ind).reset_index(drop = True)
    
    if len(check_SQL['Label'].unique()) ==1:
        # solo-class
        # save split_name
        
        detail={}
        detail['sub_list'] = sub_list
        detail['ex_list'] = ex_list
        detail['des_solo'] = des_solo
        
        coded_classes.loc[len(coded_classes)] = ['',name,'',check_SQL.loc[0,'Label'],1,feat_names,detail]
        
        i_name += 1
        continue
    elif len(check_SQL['Label'].unique()) ==0:
        detail={}
        detail['sub_list'] = sub_list
        detail['ex_list'] = ex_list
        detail['des_solo'] = des_solo
        
        coded_classes.loc[len(coded_classes)] = ['',name,'',[],0,feat_names,detail]
        
        i_name += 1
        continue


    
    fails_mat = check_SQL[feat_names].to_numpy()
    
    ind_label = len(feat_names)-1;
    X = fails_mat[:,:ind_label]
    y = fails_mat[:,ind_label]
    
    clf_all = DecisionTreeClassifier(random_state = 0, min_samples_leaf = 2)
    clf_all.fit(X, y)
    score = clf_all.score(X, y)
    
    detail={}
    detail['sub_list'] = sub_list
    detail['ex_list'] = ex_list
    detail['des_solo'] = des_solo
        
    coded_classes.loc[len(coded_classes)] = ['',name,clf_all,check_SQL['Label'].unique(), score,feat_names,detail]
    
    i_name += 1

coded_classes['score'] = [round(a,3) for a in coded_classes['score']]

pickle.dump({'coded_classes':coded_classes,'label_dic':label_dic,'server_dic':server_dic}, open(save_file, 'wb'))

print ('\n Finished \n')

break
# %% visualizing a chosen DT classifier
i_clf = 3

clf = coded_classes.loc[i_clf,'classifier']
class_names = [str(a) for a in coded_classes.loc[i_clf,'label']]

fig, ax = plt.subplots(figsize=(40,10))
#tree.plot_tree(clf, filled=True, feature_names = feat_names, ax = ax , class_names = True);
#tree.plot_tree(clf, filled=True, feature_names = feat_names, ax = ax , class_names = list(class_names.values()));
tree.plot_tree(clf, filled=True, feature_names = feat_names, ax = ax , class_names = class_names);