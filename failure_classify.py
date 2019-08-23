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
feat_names = ['checkstatus','consecutiveFails','dsc247',
                                              'checkid','Label']
fails_mat = fails_select[feat_names].to_numpy()
#np.c_[fails_mat,np.array(fails_select['servertime'])]
X = fails_mat[:,0:4]
y = fails_mat[:,4]
datasets = (X,y)
# %% classificaiton
class_names = {1:'Normal', 2: 'High', 3: 'ignore', 4:'on watch', 5:'nan'}
#X=StandardScaler().fit_transform(X)
#X[:,3] = StandardScaler().fit_transform(X[:,3].reshape(-1,1)).reshape(1,-1)
X_train, X_test, y_train, y_test = \
        train_test_split(X,y,test_size = .2, random_state = 42)

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
# %%
    i = 1;
    print("Labels:", np.unique(y_test),', names: ',[class_names[x] for x in np.unique(y_test)])
#fails_select.columns[[int(x) for x in np.unique(y_test)]
#figure = plt.figure(figsize=(10,7))
#for name, clf in zip(names,classifiers):
#        ax = plt.subplot(1, len(classifiers) + 1, i)
    name , clf = names[4], classifiers[4]
    clf = DecisionTreeClassifier(random_state = 0, min_samples_leaf = 10)
#    clf = RandomForestClassifier(n_estimators= 250,random_state = 0)
    clf.fit(X_train,y_train)
    score = clf.score(X_test, y_test)
    print(name,' score : ',score)
        
    y_pred = clf.predict(X_test)
    print(metrics.confusion_matrix(y_test,y_pred, labels = np.unique(y_test)))
    metrics.confusion_matrix(y_test,y_pred, labels = np.unique(y_test))
    
    clf.fit(X,y)
    figure = plt.figure(figsize=(20,10))
    tree.plot_tree(clf, filled=True, feature_names = feat_names, class_names = list(class_names.values()));

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


