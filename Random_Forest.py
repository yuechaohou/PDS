
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler  
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler


# In[2]:


def get_data_labels(movie_data):
    features = movie_data.drop(['rois', 'gross', 'name'], axis=1)
    rois = list(movie_data['rois'])
    gross = list(movie_data['gross'])
    features_tag = features.columns
    features = StandardScaler().fit_transform(features)
    return features, features_tag, rois, gross

def get_train_test_data(features, labels):
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.5, stratify=labels, random_state=1234)
    return X_train, X_test, y_train, y_test


# In[10]:


def RunRandomForest( X_train, X_test, y_train, y_test):
    rf = RandomForestClassifier(n_estimators=200, oob_score=True, random_state=123456)
    rf.fit(X_train, y_train)
    predicted = rf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted)

    probability = rf.predict_proba(X_test)
    
    return rf, accuracy, probability



# In[4]:


# Libraries
import matplotlib.pyplot as plt
from math import pi
from matplotlib import pyplot
 
def radar_plt_fimp(rf, features):
    # Set data
    featue_importance = list(zip(features, rf.feature_importances_))
    
    categories = []
    imp_val = []
    for imp in featue_importance:
        categories.append(imp[0])
        imp_val.append(imp[1])

    N = len(categories)

    # We are going to plot the first line of the data frame.
    # But we need to repeat the first value to close the circular graph:
    # values=df.loc[0].drop('group').values.flatten().tolist()
    imp_val += imp_val[:1]
    # print(values)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    pyplot.figure(figsize=(10, 10))
    ax = plt.subplot(111,polar=True)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='black', size=15)

    # Draw ylabels
    ax.set_rlabel_position(5)
    plt.yticks([0.1,0.2,0.3], ["0.1","0.2","0.3"], color="black", size=15)
    plt.ylim(0,0.3)

    # Plot data
    ax.plot(angles, imp_val, linewidth=1, linestyle='solid')

    # Fill area
    ax.fill(angles, imp_val, 'b', alpha=0.1)



# In[7]:


#****** MLPClassifier  ******#
from sklearn.neural_network import MLPClassifier

def RunMLPClassifier( X_train, X_test, y_train, y_test):
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(20, ), random_state=1)
    clf.fit(X_train, y_train)    
    predicted = clf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted)
    return clf, accuracy
    


# In[8]:


#****** SVM  ******#
from sklearn.svm import LinearSVC

def RunLinearSVC(X_train, X_test, y_train, y_test):
    svc = LinearSVC(random_state=3)
    svc.fit(X_train, y_train)   
    predicted = clf.predict(X_test)
    accuracy = accuracy_score(y_test, predicted)
    return svc, accuracy
    
