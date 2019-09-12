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
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
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

import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials 

os.chdir('C:\\101_task')

# %% importing annotated data from excell file
#from gspread_pandas import Spread
#Spread.sheet_to_df

head_ind=8        # index of the header
label_col = 14

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("Checks list").sheet1

#read the label column from the spreadsheet
label_list = sheet.col_values(label_col)

labeled_rows = list(filter(lambda x: label_list[x] != '', range(head_ind,len(label_list))))
labeled_rows = [int(x) for x in labeled_rows]

#fails_select = sheet.row_values(8)
headers = sheet.row_values(head_ind)
all_values = sheet.get_all_values()
fails  = pd.DataFrame([all_values[i] for i in labeled_rows] , columns = headers)

    
#reading from excel
#book = load_workbook(excel_path)
#last_row = book['Sheet1'].max_row
#print("%d rows in the excel file" % last_row)
#fails = pd.read_excel(excel_path, header = 7)
#fails.fillna('', inplace=True)
#fails.dtypes
#fails['excel_row'] = fails.index+9
#fails = fails.drop(fails[fails['Label']==''].index).reset_index(drop = True)
#fails = fails.drop(fails[fails['device_name']==''].index).reset_index(drop = True)

# %% quantifying the features + combine with checkDB
load_file = 'check_extraction.sav'
loaded_data = pickle.load( open(load_file, "rb" ))
check_DB = loaded_data['check_DB']

#fails.drop(['description', 'servertime', 'device_name'])
fails_select1 = pd.DataFrame(fails, columns = ['checkstatus','consecutiveFails','dsc247',
                                              'checkid','deviceid','Label','servertime',
                                              'description','extra'])

fails_select2 = pd.DataFrame(check_DB, columns = ['checkstatus','consecutiveFails','dsc247',
                                              'checkid','deviceid','Label','servertime',
                                              'description','extra'])

#fails_select = pd.concat([fails_select1,fails_select2], ignore_index = True)
fails_select = fails_select1.copy()   # only not definite cases


check_drp = (fails_select['checkstatus']=='')|(fails_select['checkstatus']=='add')|(fails_select['Label']=='4')
fails_select = fails_select.drop(fails_select[check_drp].index).reset_index(drop = True)

#fails_select1['Label'] = fails_select1['Label'].apply(pd.to_numeric, errors='coerce')


# convert strings to numbers
check_stats = ['testerror','testalertdelayed','testcleared','test_inactive', 
             'testok_inactive','testerror_inactive','testok']
check_dic={}
for value in range(0,len(check_stats)):
    check_dic[check_stats[value]] = value+1

fails_select['checkstatus']=list(map(lambda x:check_dic[x],fails_select['checkstatus']))
fails_select['servertime'] = [np.datetime64(a).astype(datetime) for a in fails_select['servertime']]

#fails_select['servertime'] = list(map(lambda x: np.datetime64(x).astype(datetime),fails_select['servertime']))
#time_index = list(map(lambda x: np.datetime64(x).astype(datetime),fails_select['servertime']))
fails_select[['deviceid','checkid',
              'dsc247','consecutiveFails']] = fails_select[['deviceid','checkid',
                                          'dsc247','consecutiveFails']].apply(pd.to_numeric, errors='coerce')

# ----------------- quantify check description
check_names = fails_select.description.unique()
#{key:value for (key,value) in check_list}
check_list = {}
for value in range(0,len(check_names)):
    check_list[check_names[value]] = value+1
fails_select = fails_select.drop('checkid', axis = 1)
fails_select['checkid'] = [check_list[i] for i in fails_select['description']]
check_list_inv = {k:v for (v,k) in check_list.items()}

# only H and nH:
#fails_select.loc[(fails_select['Label']=='3') | (fails_select['Label']=='1'),'Label'] = 'nH'
#fails_select.loc[fails_select['Label']=='2','Label'] = 'H'

# %% to numpy conversion
#feat_names = ['checkstatus','consecutiveFails','dsc247','checkid','Label']
feat_names = ['checkstatus','consecutiveFails','dsc247','checkid']
fails_mat = fails_select[feat_names].to_numpy()
#np.c_[fails_mat,np.array(fails_select['servertime'])]
X = fails_mat[:,0:4].copy()
#X = np.delete(X, [range(3)] , axis = 1)
#X[X[:,1]>1,1] = 2


#y = fails_mat[:,4].copy()
y = fails_select['Label'].to_numpy()

#y[y<4] = 1;
#y[y==4] = 2;

#class_names = {1:'Normal', 2: 'High', 3: 'ignore', 4:'on watch', 5:'nan'}
#class_names = {1:'Normal', 2:'on watch'}
class_names = {'nH':'not High', 'H':'High'}

datasets = (X,y)
# %% classificaiton
#X, y = datasets

# only H and nH:
y[(y=='3') | (y=='1')] = 'nH'
y[y=='2'] = 'H'
#---------- knowledge based classification: pre-annot list
#HERE!!

#---------- model training

#X=StandardScaler().fit_transform(X)
#X[:,3] = StandardScaler().fit_transform(X[:,3].reshape(-1,1)).reshape(1,-1)
X_train, X_test, y_train, y_test = \
        train_test_split(X,y,test_size = .2)#, random_state = 42)
#print(X_train[:4])
#X_train, X_test= \
#        np.delete(X_train, 1 , axis = 1), np.delete(X_test, 1 , axis = 1)
#X_train[X_train[:,1]>1,1] = 2
#X_test[X_test[:,1]>1,1] = 2
        
        
names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes"
#         ,"QDA"
         ]

classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025),
        SVC(gamma = 2, C=1),
        GaussianProcessClassifier(1.0* RBF(1)),
        DecisionTreeClassifier(max_depth = 10),
        RandomForestClassifier(max_depth = 5, n_estimators= 10, max_features = 1),
        MLPClassifier(alpha=1, max_iter=1000),
        AdaBoostClassifier(),
        GaussianNB()
#        ,QuadraticDiscriminantAnalysis()
        ]

#h = .02  # step size in the mesh
#  %%    
i = 1;
print("Labels:", np.unique(y_test),', names: ',[class_names[x] for x in np.unique(y_test)])
#fails_select.columns[[int(x) for x in np.unique(y_test)]
#figure = plt.figure(figsize=(10,7))
#for name, clf in zip(names,classifiers):
#        ax = plt.subplot(1, len(classifiers) + 1, i)
name , clf = names[4], classifiers[4]
clf = DecisionTreeClassifier(random_state = 0)
#    clf = DecisionTreeClassifier(random_state = 0, min_samples_leaf = 10)
#    clf = RandomForestClassifier(n_estimators= 250,random_state = 0)
clf.fit(X_train,y_train)
score = clf.score(X_test, y_test)
#score = clf.score(X_train, y_train)
print(name,' score : ',score)
    
y_pred = clf.predict(X_test)
print(metrics.confusion_matrix(y_test,y_pred, labels = np.unique(y_test)))
metrics.confusion_matrix(y_test,y_pred, labels = np.unique(y_test))
miss_ind = np.where(y_pred!=y_test)[0]
miss_ch = [check_list_inv[X_test[i,-1]] for i in miss_ind]


for i in miss_ind:      
    if X_test[i,-1] not in X_train: # no training sample
        name = list(filter(lambda item:item[1]== X_test[i,-1], check_list.items()))[0]
        print('No training for sample Nr. %d , class: %s - check: %s, ' % (i,name[0],str(y_test[i])))
#            print ('Bad check! ind = %d , checkid = %d' % (i, X_test[i]), ' Train label:',y_train[X_train.flatten() == X_test[i]])


clf.fit(X,y)
#fig, ax = plt.figure(figsize=(20,10))
fig, ax = plt.subplots(figsize=(40,10))
tree.plot_tree(clf, filled=True, feature_names = feat_names, ax = ax , class_names = list(class_names.values()))
#tree.plot_tree(clf, filled=True, feature_names = feat_names, ax = ax , class_names = ['a','b'])

#tree.plot_tree(clf)

#ax.plot(x,iris[column])

i += 1
# %%
#from sklearn import tree    


#import graphviz
#from sklearn.tree import export_graphviz

#dot_data = export_graphviz(clf, out_file=None)
#graph = graphviz.Source(dot_data) 
#graph.render("mongo") 


#dot_data = tree.export_graphviz(clf, out_file=None, 
#                      feature_names=["a","b","c","d"],
#                      class_names=["1","2","3","4"], 
#                      filled=True, rounded=True,  
#                      special_characters=True)  
#graph = graphviz.Source(dot_data)  
#graph 
#
#with open("mytree.dot") as f:
#    dot_graph = f.read()
#graphviz.Source(dot_graph)    
#
#
#
#from sklearn.tree import convert_to_graphviz
#convert_to_graphviz(tree)
#classifier_DT = DecisionTreeClassifier(max_depth = 5)
##classifier_DT = OneVsRestClassifier(DecisionTreeClassifier(max_depth = 5))
##classifier_RF = RandomForestClassifier(max_depth = 10, n_estimators= 20, max_features = 1)
#classifier_RF = RandomForestClassifier(n_estimators= 250, random_state=0)
#
#classifier_DT.fit(X_train,y_train)
#scode_DT = classifier_DT.score(X_test,y_test)
#print('Decision tree score:',scode_DT)
#
#classifier_RF.fit(X_train,y_train)
#scode_RF = classifier_RF.score(X_test,y_test)
#print('Random Forest score:',scode_RF)
#
#y_pred_DT = classifier_DT.predict(X_test)
#y_pred_RF = classifier_RF.predict(X_test)
#
#print("Labels:", np.unique(y_test))
#print(metrics.confusion_matrix(y_test,y_pred_DT, labels = np.unique(y_test)))
#metrics.confusion_matrix(y_test,y_pred_RF, labels = np.unique(y_test))
#
#
#classifier_DT.fit(X,y)


# %%feature relevance
importance = classifier_RF.feature_importances_
std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis = 0)

indices = np.argsort(importance)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(X.shape[1]):
    print("%d. feature %d (%f)" % (f+1,indices[f],importance[indices[f]]))

plt.figure()
plt.title("Feature importances")
plt.bar(range(X.shape[1]), importance[indices],
        color="r", yerr=std[indices], align="center")
plt.xticks(range(X.shape[1]),indices)
plt.xlim([-1, X.shape[1]])
#plt.title('Extra_trees')
plt.title('Random Forest')
plt.show()

# %% Visualization PCA / LDA / TSNE
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
plt.close('all')
Xc = np.copy(X);

yc=y.copy();

target_names = list(class_names.values())


Xc[Xc[:,1]>12,1]= 12;
yc[yc!=4]=1
yc[yc==4]=2
target_names = [target_names[0],target_names[3]]

pca = PCA(n_components = 2, whiten = False)
X_r = pca.fit(Xc).transform(Xc)

lda = LinearDiscriminantAnalysis(n_components=2)
X_r2 = lda.fit(Xc,yc).transform(Xc)
if X_r2.shape[1]==1:
    X_r2=np.insert(X_r2,1,1,axis=1)
# Percentage of variance explained for each components
print('explained variance ratio (first two components): %s'
      % str(pca.explained_variance_))

fig1 = plt.figure()
colors = ['navy', 'turquoise', 'darkorange', 'green']
lw = 2

for color, i, target_name in zip(colors,range(1,int(yc.max())+1), target_names):
    plt.scatter(X_r[yc == i ,0], X_r[yc == i ,1], color = color, alpha = 0.8 , 
                lw = lw, label = target_name)
plt.legend(loc='best', shadow=False, scatterpoints=1)
plt.title('PCA of data')
#plt.xscale('linear')
ax = fig1.add_subplot(111);
for i, xy in zip(range(1,len(X_r)+1),X_r):
    ax.annotate('% s' % i, xy = xy, textcoords = 'data') 


fig2 = plt.figure(2)
for color, i, target_name in zip(colors, range(1,int(yc.max())+1), target_names):
    plt.scatter(X_r2[yc == i, 0], X_r2[yc == i, 1], alpha=.8, color=color,
                label=target_name)
ax = fig2.add_subplot(111);
#for i, xy in zip(range(1,len(X_r)+1),X_r):
#    ax.annotate('% s' % i, xy = xy, textcoords = 'data')
    
plt.legend(loc='best', shadow=False, scatterpoints=1)
#plt.xscale('log')
plt.xscale('linear')
plt.title('LDA of data')



plt.show()
