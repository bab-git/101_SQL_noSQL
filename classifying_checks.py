# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 09:57:49 2019

@author: Babak Hosseini
"""

print(__doc__)
import numpy as np

import matplotlib.pyplot as plt

from sklearn.datasets import make_multilabel_classification
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.decomposition import PCA

#def plot_hyperplane(clf, min_x, max_x, linestyle, label):


def plot_hyperplane(clf, min_x, max_x, linestyle, label):
    # get the separating hyperplane
    w = clf.coef_[0]
    a = -w[0] / w[1]
    xx = np.linspace(min_x - 5, max_x + 5)  # make sure the line is long enough
    yy = a * xx - (clf.intercept_[0]) / w[1]
    plt.plot(xx, yy, linestyle, label=label)
    
    
X, Y = make_multilabel_classification(n_classes=2,n_labels=1,allow_unlabeled=True,random_state=1)

plt.figure(figsize=(8,6))

X = PCA(n_components=2).fit_transform(X)

min_x = min(X[:,0])
max_x = max(X[:,0])

min_y = min(X[:,1])
max_y = max(X[:,1])

classif = OneVsRestClassifier(SVC(kernel='linear'))
classif.fit(X,Y)

plt.subplot(2,2, 1)
plt.title("test 1")

zero_class = np.where(Y[:,0])
one_class = np.where(Y[:,1])
plt.scatter(X[:,0],X[:,1], s=40, c='gray')
plt.scatter(X[zero_class,0],X[zero_class,1], s=160, edgecolors='b',
                facecolors='none', linewidths=2, label='Class 1')
plt.scatter(X[one_class,0],X[one_class,1], s=160, edgecolors='orange',
                facecolors='none', linewidths=2, label='Class 2')

plot_hyperplane(classif.estimators_[0], min_x, max_x, 'k--', 'Bouindry\nfor class 1')
plot_hyperplane(classif.estimators_[1], min_x, max_x, 'k-.', 'Boundary\nfor class 2')

plt.xticks(())
plt.yticks(())
plt.xlim(min_x - .5 * max_x, max_x + .5 * max_x)
plt.ylim(min_y - .5 * max_y, max_y + .5 * max_y)

Z = classif.predict(X)
classif.score(X,Y)
plt.legend(loc='upper left')