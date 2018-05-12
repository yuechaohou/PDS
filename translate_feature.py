
# coding: utf-8

# In[1]:


from feature_selection import movie
from feature_selection import scraper_rotten_tomatoes
import os
import pickle
import seaborn as sns
from multiprocessing import Pool
from datetime import datetime
import numpy as np
import operator
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

sns.set(color_codes=True)


def is_released(movie_name, movie_infos):
    if 'Domestic Releases' not in movie_infos[movie_name]['summary']:
        return False
    elif len(movie_infos[movie_name]['summary']['Domestic Releases'].keys()) == 0:
        return False
    else:
        release = movie_infos[movie_name]['summary']['Domestic Releases']
        if 'Wide' in release and release['Wide'] > datetime.now():
            return False
        elif 'IMAX' in release and release['IMAX'] > datetime.now():
            return False
        elif 'Limited' in release and release['Limited'] > datetime.now():
            return False
        else:
            return True

# get the names of all the movie
def get_movie_names_all():
    with open('movie_info.pkl', 'rb') as f:
        movie_infos = pickle.load(f)
    count = 0
    movie_names = list(movie_infos.keys())
    movie_names = [movie_name for movie_name in movie_names if is_released(movie_name, movie_infos)]
    return movie_names


# In[4]:


# calculate the ROI of a movie
def get_revenue(movie_name, all_dict):
    movie_dict = all_dict[movie_name]
    if len(movie_dict['international']['Worldwide Box Office']) != 0:
        revenue = movie_dict['international']['Worldwide Box Office'][0]['Revenue']
    elif len(movie_dict['international']['International Box Office']) != 0:
        revenue = movie_dict['international']['International Box Office'][0]['Revenue']
    elif len(movie_dict['box_office']['demostic']) != 0:
        revenue = movie_dict['box_office']['demostic'][0]['Revenue']
    else:
        revenue = None
    return revenue

def get_revenues():
    movie_names = get_movie_names_all()
    
    with open('movie_info.pkl', 'rb') as f:
        movie_dict = pickle.load(f)
    
    output = []
    for movie_name in movie_names:
        revenue = get_revenue(movie_name, movie_dict)
        if revenue is not None:
            output.append( (movie_name, revenue) )
    return output
    
def get_ROI(movie_name, all_dict):
    movie_dict = all_dict[movie_name]
    budget = movie_dict['summary']['Budget']
    revenue = get_revenue(movie_name, all_dict)
    if revenue is None:
        return None
    ROI = (revenue - budget) / budget
    return ROI

def get_ROIs():
    movie_names = get_movie_names_all()
    # print(movie_names[:10])
    
    with open('movie_info.pkl', 'rb') as f:
        movie_dict = pickle.load(f)
    
    output = []
    for movie_name in movie_names:
        ROI = get_ROI(movie_name, movie_dict)
        if ROI is not None:
            output.append( (movie_name, ROI) )
    
    # output.sort(key=operator.itemgetter(1))
    # output.reverse()
    return output

# The individual difference of the ROI of each movie could be very large, ranging from -0.9999749 to 1799. With regard to the movie with exceptionally large ROI, we regard these values as outliers and give special consideration. We divide our ROI range into the following groups: [-0.9999749, 0), [0, 1), [1, 2), [2, 5), [5, 10), [10, 30), [30, ..). Now, we use this boudary to label the different movies.

# In[6]:


# categorize the movie using their ROI
def label_roi(roi):
    if roi > -1 and roi < 0:
        return 0
    elif roi >= 0 and roi < 1:
        return 1
    elif roi >= 1 and roi < 2:
        return 2
    elif roi >= 2 and roi < 5:
        return 3
    elif roi >= 3 and roi < 10:
        return 4
    elif roi >= 10 and roi < 30:
        return 5
    else:
        return 6
# label all the movies
def get_labels_roi():
    ROIs = get_ROIs()
    output = []
    for ROI in ROIs:
        roi = ROI[1]
        movie_name = ROI[0]
        label = label_roi(roi)
        output.append((movie_name, label))
    return output

def label_revenue(revenue):
    # pass
    if revenue > 0 and revenue < 1000000:
        return 0
    elif revenue >= 1000000 and revenue < 5000000:
        return 1
    elif revenue >= 5000000 and revenue < 10000000:
        return 2
    elif revenue >= 10000000 and revenue < 50000000:
        return 3
    elif revenue >= 50000000 and revenue < 100000000:
        return 4
    elif revenue >= 100000000 and revenue < 500000000:
        return 5
    elif revenue >= 500000000 and revenue < 1000000000:
        return 6
    else:
        return 7

def get_labels_revenue():
    movie_revenues = get_revenues()
    output = []
    for movie_revenue in movie_revenues:
        movie_name = movie_revenue[0]
        revenue = movie_revenue[1]
        if revenue is None:
            continue
        label = label_revenue(revenue)
        output.append( (movie_name, label) )
    return output

# get the semantics of a comment
def get_semantics(text):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(text)
    neg = ss['neg']
    neu = ss['neu']
    compound = ss['compound']
    pos = ss['pos']
    # print(neg, neu, compound, pos)
    return neg, neu, compound, pos


# prepare the data
from sklearn.preprocessing import MinMaxScaler

def get_info_with_localname(name):
    with open('movie_info.pkl', 'rb') as f:
        name_dic = pickle.load(f)
    return name_dic[name]

def get_daily_box_offices(movie_name):
    movie_info = get_info_with_localname(movie_name)
    box_offices = movie_info['box_office']['daliy']
    data = []
    for box_office in box_offices:
        data.append([box_office['Gross']])
    
    data = np.array(data)
    return data

def data_partition(data, N):
    num_rows = data.shape[0]
    x = []
    y = []
    for i in range(num_rows - N):
        temp = []
        for j in range(N):
            temp.append(data[i + j])
        x.append(np.array(temp))
        y.append(data[i + N])
    x = np.array(x)
    y = np.array(y)
    return x, y


from matplotlib import pyplot
from sklearn.preprocessing import MinMaxScaler

# In[ ]:



# In[ ]:


from sklearn.preprocessing import MinMaxScaler

def one_hot_encode(data):
    n = len(np.unique(data))
    result = np.zeros(shape=(len(data), n))
    for index, sample in enumerate(data):
        result[index][sample] = 1
    return result


def get_neural_mlc(input_dim, output_dim):
    model = Sequential()
    
    model.add(Dense(256, activation=backend.relu, input_dim=input_dim))
    # model.add(Activation('relu'))
    model.add(Dropout(0.3))
    model.add(Dense(128, activation=backend.relu))
    # model.add(Activation('relu'))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation=backend.relu))
    # model.add(Activation('relu'))
    model.add(Dropout(0.3))

    model.add(Dense(output_dim))
    model.add(Activation('softmax'))
    
    # print out the network architecture
    model.summary()
    
    model.compile(loss='categorical_crossentropy', 
              optimizer='adam',
              metrics=['accuracy'])
    
    return model

def get_model_regression(input_dim):
    model = Sequential()
    model.add(Dense(20, input_dim=input_dim, kernel_initializer='normal', activation='relu'))
    model.add(Dense(10, kernel_initializer='normal', activation='relu'))
    model.add(Dense(5, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

def run_neural_mlc(X_train, X_test, y_train, y_test, epochs):
    model = get_neural_mlc(X_train.shape[1], len(y_train[0]))
    model.fit(X_train, y_train, epochs=epochs)
    predictions = model.predict(X_test)
    count = 0
    for index, prediction in enumerate(predictions):
        # print(np.argmax(prediction), np.argmax(y_test[index]))
        count += (np.argmax(prediction) == np.argmax(y_test[index]))
    accuracy = count / len(y_test)
    return model, accuracy