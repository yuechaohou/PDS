import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle
from datetime import datetime
from sklearn.decomposition import PCA 
import math
import numpy as np

visual_list=dict()

with open('movie_info.pkl', 'rb') as f:
    movie_info=pickle.load(f)
    
with open('person_info.pkl', 'rb') as f:
    person_info=pickle.load(f)
    
with open('name_url.pkl', 'rb') as f:
    movie_budget=pickle.load(f)

visual_y=list()
visual_list['budget']=list()
visual_list['cast']=list()
total_info=dict()
key_list=['Keywords', 'Production Method', 'Franchise', 'Creative Type', 'Genre', 'Production Companies']
for key in key_list:
    file_name='_'.join(key.lower().split())
    visual_list[file_name]=list()
    with open(file_name+'.pkl','rb') as f:
        total_info[file_name]=pickle.load(f)

for name in movie_info.keys():
    cast_dic=movie_info[name]['cast']
    cast_list=['leading_members', 'production']
    if 'Keywords' in movie_info[name]['summary'].keys() and 'Production Method' in movie_info[name]['summary'].keys() \
    and 'Franchise' in movie_info[name]['summary'].keys() and 'Creative Type' in movie_info[name]['summary'].keys() \
    and 'Genre' in movie_info[name]['summary'].keys() and 'Production Companies' in movie_info[name]['summary'].keys() \
    and 'Domestic Releases' in movie_info[name]['summary'].keys() and min(movie_info[name]['summary']['Domestic Releases'].values())<datetime.now():
        
        if math.log(movie_budget[name]['Worldwide Gross']+1)<19:
            visual_y.append('r')
        elif math.log(movie_budget[name]['Worldwide Gross']+1)<20:
            visual_y.append('b')
        else:
            visual_y.append('g')
            
        tmplist=list()
        for cate in cast_list:
            if cate in cast_dic.keys():
                for person in cast_dic[cate]:
                    person_name=person['name'].strip()
                    tmplist.append(person_info[person_name])
        
        visual_list['cast'].append(np.mean(np.array(tmplist)))
        visual_list['budget'].append(movie_budget[name]['Production Budget'])
        
        key_list=['Franchise', 'Creative Type', 'Genre']
        for key in key_list:
            file_name='_'.join(key.lower().split())
            cate=movie_info[name]['summary'][key].strip()
            visual_list[file_name].append(total_info[file_name][cate])
        
        key_list=['Keywords', 'Production Method','Production Companies']
        for key in key_list:
            file_name='_'.join(key.lower().split())
            tmplist=list()
            for cate in movie_info[name]['summary'][key]:
                tmplist.append(total_info[file_name][cate.strip()])
            visual_list[file_name].append(np.mean(np.array(tmplist)))

P=np.array(list(visual_list.values())).T
visual_y=np.array(visual_y)
y_train=visual_y[~np.isnan(P).any(axis=1)]
P=P[~np.isnan(P).any(axis=1)]
pca = PCA(n_components=3)
pca.fit(P)
P=pca.transform(P)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter3D(P[:,0],P[:,1],P[:,2], c=y_train)
plt.show()