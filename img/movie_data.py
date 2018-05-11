
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


# read rating data from rating.csv
def merge_rating_impactFactors()
    rating = pd.read_csv('ratings.csv')
    rating.set_index('name', inplace=True)

    # read impact factors, roi, gross form matrix.txt
    select_movie = []
    roi = []
    gross = []

    with open("matrix.txt", "r") as f:
        data = f.readlines() 
        for line in data:
            idx2 = line.rfind(' ')
            idx1 = line[:idx2].rfind(' ')
            select_movie.append(line[:idx1])
            roi.append(int(line[idx1+1:idx2]))
            gross.append(int(line[idx2+1:]))

    # drop unused data and labels 
    select_rating = rating.loc[select_movie].drop(['plot'], axis=1)
    select_rating['rois'] = np.array(roi)
    select_rating['gross'] = np.array(gross)

    # use avg to fill NaN data
    ratting_var=["imdbRating", "Rotten_Tomatoes","Metacritic","imdbVotes"]
    for var in ratting_var:
        avg = np.mean(select_rating[var].notna())
        isNone = pd.isna(select_rating[var])
        noneList = []
        for i in range(len(isNone)):
            if isNone[i] == True:
                noneList.append(i)
        select_rating[var][noneList] = avg
        
     # read impact factor from movie_info.csv
    impact_factor = pd.read_csv('movie_info.csv')

    impact_movie = list(impact_factor['name'])
    select_set = set(select_movie)
    select_movie2 = []
    for movie in impact_movie:
        if select_set.__contains__(movie):
            select_movie2.append(movie)

    select_rating = select_rating.loc[select_movie2]
    impact_factor.set_index('name', inplace=True)
    impact_factor = impact_factor.loc[select_movie2]

    select_rating['budget'] = np.array(impact_factor['budget'])
    select_rating['cast'] = np.array(impact_factor['cast'])
    select_rating['keywords'] = np.array(impact_factor['keywords'])
    select_rating['production_method'] = np.array(impact_factor['production_method'])
    select_rating['franchise'] = np.array(impact_factor['franchise'])
    select_rating['creative_type'] = np.array(impact_factor['creative_type'])
    select_rating['genre'] = np.array(impact_factor['genre'])
    select_rating['production_companies'] = np.array(impact_factor['production_companies'])

    select_rating.to_csv('movie_data.csv')

