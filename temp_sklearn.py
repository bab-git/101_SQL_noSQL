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
from sklearn import svm, datasets, metrics

#def plot_hyperplane(clf, min_x, max_x, linestyle, label):
# %%========================

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

#%% difit classifcicaiton
digits = datasets.load_digits()

images_and_labels  = list(zip(digits.images,digits.target))

for index, (image, label) in enumerate(images_and_labels[:4]):
    plt.subplot(2,4, index + 1)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Training: %i' % label)
    
n_samples = len(digits.images)
data = digits.images.reshape((n_samples,-1))

classif = svm.SVC(gamma = 0.001)
classif.fit(data[:n_sample //2],digits.target[:n_sample //2]) 

expected = digits.target[n_sample // 2:]
predicted = classif.predict(data[n_sample // 2:])

metrics.classification_report(expected,predicted)
print ("report for clasfier %s:\n%s\n"
       %(classif,metrics.classification_report(expected,predicted)))

print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))


images_and_predictions = list(zip(digits.images[n_samples // 2:], predicted))
for index, (image, prediction) in enumerate(images_and_predictions[:4]):
    plt.subplot(2, 4, index + 5)
    plt.axis('off')
    plt.imshow(image, cmap=plt.cm.gray_r, interpolation='nearest')
    plt.title('Prediction: %i' % prediction)
    
plt.show()

#%% several classifiers
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.datasets import make_classification, make_moons, make_circles
from sklearn.preprocessing import StandardScaler
from matplotlib.colors import ListedColormap

h = .02  # step size in the mesh
names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025),
        SVC(gamma = 2, C=1),
        GaussianProcessClassifier(1.0* RBF(1)),
        DecisionTreeClassifier(max_depth = 5),
        RandomForestClassifier(max_depth = 5, n_estimators= 10, max_features = 1),
        MLPClassifier(alpha=1, max_iter=1000),
        AdaBoostClassifier(),
        GaussianNB(),
        QuadraticDiscriminantAnalysis()]

x, y = make_classification(n_features = 2, n_redundant=0, n_informative=2,
                           random_state=1,n_clusters_per_class=1)
plt.scatter(x[:,0],x[:,1], s=160, edgecolors='b',
                facecolors='none', linewidths=2, label='Class 1')

rng = np.random.RandomState(2)
x += 2* rng.uniform(size = x.shape)

plt.scatter(x[:,0],x[:,1], s=160, edgecolors='r',
                facecolors='none', linewidths=2, label='Class 1')

linearly_separable = (x,y)

datasets = [make_moons(noise=0.3, random_state=0),
            make_circles(noise=0.2, factor=0.5, random_state=1),
            linearly_separable
            ]
figure = plt.figure(figsize=(16,7))
i = 1
for ds_cnt, ds in enumerate(datasets):
    x,y = ds
    x = StandardScaler().fit_transform(x)
    X_train, X_test, y_train, y_test = \
        train_test_split(x,y,test_size = .4, random_state = 42)
    x_min , x_max = x[:,0].min() - 0.5 , x[:,0].max() - 0.5
    y_min, y_max = x[:, 1].min() - .5, x[:, 1].max() + .5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                           np.arange(y_min, y_max, h))
    
    cm = plt.cm.RdBu
    cm_bright = ListedColormap(['#FF0000', '#0000FF'])
    ax = plt.subplot(len(datasets), len(classifiers)+1,i)

    if ds_cnt == 0:
        ax.set_title("Input data")
    ax.scatter(X_train[:,0],X_train[:,1],c = y_train,cmap=cm_bright, alpha=0.6,
               edgecolors='k')
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    ax.set_xticks(())
    ax.set_yticks(())

    i += 1
    
    for name, clf in zip(names,classifiers):
        ax = plt.subplot(len(datasets), len(classifiers) + 1, i)
        clf.fit(X_train,y_train)
        score = clf.score(X_test, y_test)
        
        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, x_max]x[y_min, y_max].
        if hasattr(clf,'decision_function'):
            Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        else:
            Z = clf.predict_proba(np.c_[xx.ravel(),yy.ravel()])[:,1]
        
        # Put the result into a color plot        
        Z = Z.reshape(xx.shape)
        ax.contourf(xx,yy,Z,cmap=cm, alpha=.8)
        
        # Plot the training points
        ax.scatter(X_train[:,0],X_train[:,1], c = y_train, cmap=cm_bright,
                   edgecolors='k')
        
        # Plot the testing points
        ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright,
                   edgecolors='k', alpha=0.6)
        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())
        if ds_cnt == 0:
            ax.set_title(name)
        ax.text(xx.max() - .3, yy.min() + .3, ('%.2f' % score).lstrip('0'),
                size=15, horizontalalignment='right')
        i += 1
plt.tight_layout()
plt.show()        
# %% feature relevanc by forest trees 
from sklearn.ensemble import ExtraTreesClassifier

x, y = make_classification(n_samples = 1000, n_features = 10, n_informative = 3, n_redundant = 0,
                           n_repeated = 0, n_classes =2 , random_state =0 , shuffle = 0) 

# Build a forest and compute the feature importances
#forest = ExtraTreesClassifier(n_estimators = 250, random_state = 0)
forest = RandomForestClassifier(n_estimators= 250, random_state = 0)

forest.fit(x,y)
importance = forest.feature_importances_
std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis = 0)
indices = np.argsort(importance)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(x.shape[1]):
    print("%d. feature %d (%f)" % (f+1,indices[f],importance[indices[f]]))

plt.figure()
plt.title("Feature importances")
plt.bar(range(x.shape[1]), importance[indices],
        color="r", yerr=std[indices], align="center")
plt.xticks(range(x.shape[1]),indices+1)
plt.xlim([-1, x.shape[1]])
#plt.title('Extra_trees')
plt.title('Random Forest')
plt.show()