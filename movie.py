
# coding: utf-8

# In[1]:


# setup library imports
import io, time, json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pickle
from collections import Counter
import html
from datetime import datetime
from multiprocessing import Pool


# In[2]:


#helper function to locate the location of interest
def find_helper(root, tag, content, ty='movie'):
    hs=root.find_all(tag)
    details=None
    for h in hs:
        if h.get_text()==content:
            if ty != 'person':
                details = h.find_next()
            else:
                 details = h.find_next().find_next()
            break
            
    return details
    pass


# In[3]:


#helper function to parse the table
def table_helper(root, titles, tag, content):
    table_details = find_helper(root, tag, content)
    
    #get the table list
    table_list=list()
    
    if table_details==None:
        return table_list
    else:
        table_details=table_details.table
        if table_details==None:
            return table_list
        
        
    for row in table_details.find_all("tr"):
        i=0
        table_dic=dict()
        for column in row.find_all("td"):
            if titles[i]!='Date':
                if titles[i]=='Change':
                    if len(table_list)==0:
                        table_dic['Change']=0.0
                    else:
                        try:
                            table_dic['Change']=float(column.get_text().replace(u'\xa0', u' ').strip('%'))/100
                        except:
                            table_dic['Change']='-'
                else:
                    if column.get_text().replace(u'\xa0', u' ')=='-':
                        table_dic[titles[i]]='-'
                    else:
                        try:
                            table_dic[titles[i]]=int(column.get_text().replace(u'\xa0', u' ').replace('$','').replace(',',''))
                        except:
                            table_dic[titles[i]]=html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
                            pass
            else:
                try:
                    table_dic[titles[i]]=datetime.strptime(html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r',''), '%Y/%m/%d')
                except:
                    table_dic[titles[i]]='-'
            i+=1
                
        if len(table_dic)>0:
            table_list.append(table_dic)
                
    return table_list


# In[4]:


#helper function to parse the center table
def center_table_helper(root, titles, tag, content, ty='movie'):
    table_details = find_helper(root, tag, content, ty)
        
    #get the center table list
    table_list=list()
    
    if table_details==None:
        return table_list
    else:
        table_details=table_details.table
        if table_details==None:
            return table_list
        
    for row in table_details.find_all("tr"):
        i=0
        isend=False
        table_dic=dict()
        if len(row.find_all("td"))==len(titles):
            for column in row.find_all("td"):
                if titles[i]=='Chart Date':
                    try:
                        table_dic[titles[i]]=datetime.strptime(html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','').strip(), '%b %d, %Y')
                    except:
                        table_dic[titles[i]]='-'
                        isend=True
                        break
                elif titles[i]=='Release Date' or titles[i]=='Report Date':
                    try:
                        table_dic[titles[i]]=datetime.strptime(html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r',''), '%m/%d/%Y')
                    except:
                        table_dic[titles[i]]='-'
                        isend=True
                        break
                elif titles[i]=='Domestic Share':
                    try:
                        table_dic[titles[i]]=float(html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('%',''))/100
                    except:
                        table_dic[titles[i]]='-'
                elif (not titles[i].startswith('Record'))  and (not titles[i].startswith('Role')) and (not titles[i].startswith('Title')) and (not titles[i].startswith('Report')) and (not titles[i].startswith('Chart')) and (not titles[i].startswith('Territory')) and (not titles[i].startswith('Release')) and titles[i]!='':
                    if column.get_text().replace(u'\xa0', u' ')=='-':
                        table_dic[titles[i]]=-1
                    else:
                        try:
                            table_dic[titles[i]]=int(column.get_text().replace(u'\xa0', u' ').replace('$','').replace(',',''))
                        except:
                            table_dic[titles[i]]=html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
                            pass
                else:
                    if titles[i]!='':
                        table_dic[titles[i]]=html.unescape(column.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
                i+=1
        if isend:
            break
        if len(table_dic)>0:
            table_list.append(table_dic)
    
    return table_list


# In[31]:


#helper function to parse the table in cast tab
def cast_table_helper(root, tag, content):
    details=find_helper(root, tag, content)
    host_url="https://www.the-numbers.com"
    
    #is_First=True
    table_list=list()
    
    if details==None:
        return table_list
    
    for a in details.find_all('a'):
        table_dic=dict()
        table_dic['name']=html.unescape(a.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','').strip()
        table_dic['url']=host_url+a.get('href')
        if content=='Production and Technical Credits':
            if a.span:
                table_dic['role']=text1=html.unescape(a.find_next().find_next().find_next().get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','').strip()
            else:
                table_dic['role']=html.unescape(a.find_next().find_next().get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','').strip()
        table_list.append(table_dic)
    
    return table_list


# In[6]:


#helper function
#given the html content, return the information as a dictionary
def parse_page(html_page, title):
    root=BeautifulSoup(html_page.decode('utf-8'), "html.parser")
    lis=dict()
    if title=="summary":
        #get the table tag of the movie details
        details = find_helper(root, 'h2', 'Movie Details')
        
        if details==None:
            return lis
        
        #get the information of the movie
        for item in details.find_all("tr"):
            first_child = item.contents[0]
            second_child = first_child.find_next_sibling()
            c_name = html.unescape(first_child.b.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
            if c_name.endswith('Budget:'):
                try:
                    lis['Budget'] = int(second_child.get_text().replace(u'\xa0', u' ').replace('\n','').replace('\r','').replace('$','').replace(',',''))
                except:
                    lis['Budget'] = html.unescape(second_child.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
                    pass
                
            elif c_name.startswith("Domestic"):
                text=second_child.prettify().split('<br/>')
                sub_dic=dict()
                for cate in text:
                    cate_temp = cate.split(')')[0].split('(')
                    date_data=html.unescape(cate_temp[0]).replace('<td>','').replace('\n','').replace('\r','').replace('by','').strip()
                    if len(date_data.split(','))>1:
                        date_type=date_data.split(',')[0][-2:]
                        try:
                            sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%B %d'+date_type+', %Y')
                        except:
                            sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%B, %Y')
                    else:
                        if len(date_data.split())==1:
                            sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%Y')
                        else:
                            sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data.split()[1], '%Y')
                    
                lis['Domestic Releases'] = sub_dic
                
            elif c_name.startswith('International'):
                text = second_child.get_text().replace(u'\xa0', u' ').split('\n')
                sub_dic=dict()
                for cate in text:
                    cate_temp = cate.replace(')','').split('(')
                    if len(cate_temp)>2:
                        temp_key = cate_temp[2].strip()
                        if temp_key in sub_dic.keys():
                            temp_dic=sub_dic[temp_key]
                        else:
                            temp_dic=dict()
                        
                        date_data=html.unescape(cate_temp[0]).replace('<td>','').replace(u'\xa0', u' ').replace('\n','').replace('\r','').replace('Week of','').strip()
                        if len(date_data.split(','))>1:
                            date_type=date_data.split(',')[0][-2:]
                            try:
                                sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%B %d'+date_type+', %Y')
                            except:
                                sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%B, %Y')
                        else:
                            sub_dic[cate_temp[1].strip()] = datetime.strptime(date_data, '%Y')
                
                lis['International Releases']=sub_dic
            
            elif c_name.startswith('Video'):
                text=html.unescape(second_child.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','').split('by')
                if len(text[0].split(','))>1:
                    date_type=text[0].split(',')[0][-2:]
                    try:
                        lis['Video Release']=datetime.strptime(text[0].strip(), '%B %d'+date_type+', %Y')
                    except:
                        try:
                            lis['Video Release']=datetime.strptime(text[0].strip(), '%B, %Y')
                        except:
                            temp=text[0].split(',')
                            date_type=temp[0][-2:]
                            lis['Video Release']=datetime.strptime(temp[0]+','+temp[1], '%B %d'+date_type+', %Y')
                            
                else:
                    lis['Video Release']=datetime.strptime(text[0].strip(), '%Y')
                
                
            elif c_name.startswith('MPAA'):
                lis['MPAA Rating']=html.unescape(second_child.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
            
            elif c_name.startswith('Comparisons'):
                pass
            
            elif c_name.startswith('Keywords'):
                lis['Keywords']=second_child.get_text().replace(u'\xa0', u' ').split(',')
            
            elif c_name.startswith('Creative'):
                lis['Creative Type']=html.unescape(second_child.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
                
            elif c_name.startswith('Production Countries') or c_name.startswith('Production Companies'):
                lis[c_name.replace(':','')]=html.unescape(second_child.get_text()).replace(u'\xa0', u' ').split(',')
            
            elif c_name.startswith('Production Method'):
                lis['Production Method']=second_child.get_text().replace(u'\xa0', u' ').split('/')
                 
            else:
                lis[c_name.replace(':','')]=html.unescape(second_child.get_text()).replace(u'\xa0', u' ').replace('\n','').replace('\r','')
            pass
        

        #The column name
        title_name=['Record', 'Rank', 'Amount', 'Chart Date', 'Days In Release']
        
        #get the rank list
        lis['ranking on other records']=center_table_helper(root, title_name, 'h3', 'Ranking on other Records and Milestones')
                
    
    elif title=="box_office":
        #The column name
        title_name=['Record', 'Rank', 'Revenue']
        #get the demostic table information
        lis['demostic']=center_table_helper(root, title_name, 'h2', 'Domestic Cumulative Box Office Records')
        
        #get the weekend box office performance
        weekend_title=['Date', 'Rank', 'Gross', 'Change', 'Theaters', 'Per Theater', 'Total Gross', 'Week']
        lis['weekend']=table_helper(root, weekend_title, 'h2', 'Weekend Box Office Performance')
        
        #get the daliy box office performance
        daliy_title=['Date', 'Rank', 'Gross', 'Change', 'Theaters', 'Per Theater', 'Total Gross', 'Day']
        lis['daliy']=table_helper(root, weekend_title, 'h2', 'Daily Box Office Performance')
        
        #get the weekly box office performanc
        weekly_title=['Date', 'Rank', 'Gross', 'Change', 'Theaters', 'Per Theater', 'Total Gross', 'Week']
        
        lis['weekly']=table_helper(root, weekend_title, 'h2', 'Weekly Box Office Performance')
        pass
    
    
    elif title=="international":
        title_name=['Territory', 'Release Date', 'Opening Weekend', 'Opening Weekend Theaters', 'Maximum Theaters', 'Theatrical Engagements', 'Total Box Office', 'Report Date']
        #get the box office summary
        lis['Box Office Summary']= center_table_helper(root, title_name, 'h2','Box Office Summary Per Territory')
        
        title_name=['Record', 'Rank', 'Revenue']
        #get the international box office
        lis['International Box Office']=center_table_helper(root, title_name, 'h2', 'International Cumulative Box Office Records')
        
        title_name=['Record', 'Rank', 'Revenue']
        lis['Worldwide Box Office']=center_table_helper(root, title_name, 'h2', 'Worldwide Cumulative Box Office Records')
        pass
    
    
    elif title=="news":
        host_url="https://www.the-numbers.com"
        url_list=list()
        for item in root.find_all('a'):
            if item.get_text().replace(u'\xa0', u' ')=='More...':
                url_list.append(host_url+item.get('href'))
                
        text_list=list()
        for url in url_list:
            try:
                url_response=requests.get(url)
            except:
                continue
            url_html=url_response.content
            url_root=BeautifulSoup(url_html.decode('utf-8'), "html.parser")
            for div in url_root.find_all('div'):
                if div.get('id')=='news':
                    news_content=html.unescape(div.get_text()).replace('\n',' ').replace('\r', '').replace(u'\xa0', u' ')
                    text_list.append(news_content)
                    break

        lis['news']=text_list
        pass
    
    elif title=="cast":
        lis['leading_members']=cast_table_helper(root, 'h1', 'Lead Ensemble Members')
        lis['supporting_cast']=cast_table_helper(root, 'h1', 'Supporting Cast')
        lis['cameos']=cast_table_helper(root, 'h1', 'Cameos')
        lis['uncategorized']=cast_table_helper(root, 'h1', 'Uncategorized')
        lis['production']=cast_table_helper(root, 'h1', 'Production and Technical Credits')
        pass
            
    return lis


# In[7]:


#helper function
#given the url of the movie, get all the information of the movie
#https://www.the-numbers.com/movie/Black-Panther#tab=summary
def get_info(url):
    summary_url=url+"#tab=summary"
    international_url=url+"#tab=international"
    box_office_url=url+"#tab=box-office"
    news_url=url+"#tab=news"
    cast_url=url+"#tab=cast-and-crew"
    
    summary_response = requests.get(summary_url)
    international_response = requests.get(international_url)
    box_office_response = requests.get(box_office_url)
    news_response = requests.get(news_url)
    cast_response = requests.get(cast_url)
    summary_dic, international_dic, box_office_dic, news_dic, cast_dic = dict(), dict(), dict(), dict(), dict()
    
    if summary_response.status_code != 404:
        summary_dic = parse_page(summary_response.content, "summary")
        #pprint(summary_dic)
    
    if international_response.status_code != 404:
        international_dic = parse_page(international_response.content, "international")
        #pprint(international_dic)
    
    if box_office_response.status_code != 404:
        box_office_dic = parse_page(box_office_response.content, "box_office")
        #pprint(box_office_dic)
        
    if news_response.status_code !=404:
        news_dic=parse_page(news_response.content, "news")
        ##print(len(news_dic['news']))
        #pprint(news_dic)
        
    if cast_response.status_code!=404:
        cast_dic=parse_page(cast_response.content, "cast")
        #pprint(cast_dic)
        
    total_dic=dict()
    total_dic['summary']=summary_dic
    total_dic['international']=international_dic
    total_dic['box_office']=box_office_dic
    total_dic['news']=news_dic
    total_dic['cast']=cast_dic
    
    return total_dic


# In[15]:


# In[8]:


#function to get the dictionary of {name:url}
#The result is saved in name_url.pkl, no need to run it
#https://www.the-numbers.com/movie/budgets/all/5501
#The structure of the dictionary is as following:
#{name of movie: {'url': string,
#                  'Release Date': datetime,
#                  'Production Budget': int,
#                  'Domestic Gross': int, 
#                   'Worldwide Gross': int}, ....}
def extract_url_dic():
    url='https://www.the-numbers.com/movie/budgets/all/'
    count=1
    name_dic={}
    titles=['Release Date', 'Movie', 'Production Budget', 'Domestic Gross', 'Worldwide Gross']
    host_url='https://www.the-numbers.com'
    while count<5601:
        page_url=url+str(count)
        page_response=requests.get(page_url)
        root=BeautifulSoup(page_response.content.decode('utf-8'), "html.parser")
        
        table=root.table
        tr=table.find_all('tr')[1]
        i=0
        temp_dic={}
        name=None
        for td in tr.find_all('td'):
            if i>0:
                if titles[i-1]=='Movie':
                    name=html.unescape(td.get_text()).replace(u'\xa0', u' ').strip()
                    temp_dic['url']=host_url+td.a.get('href').replace('#tab=summary','')
                elif titles[i-1].startswith('Release'):
                    year=td.get_text().replace(u'\xa0', u' ').split('/')[2]
                    temp_dic[titles[i-1]]=datetime.strptime(html.unescape(td.get_text()).replace(u'\xa0', u' '),'%m/%d/%Y')
                else:
                    try:
                        temp_dic[titles[i-1]]=int(td.get_text().replace(u'\xa0', u' ').replace('$','').replace(',',''))
                    except:
                        temp_dic[titles[i-1]]=html.unescape(td.get_text()).replace(u'\xa0', u' ')
                        pass
            i+=1
            if i==len(titles)+1:
                i=0
                if name!=None:
                    print(name+'('+year+ ')')
                    #print(temp_dic)
                    name_dic[name+'('+year+ ')']=temp_dic
                    name=None
                    temp_dic={}
                    
        count+=100
        #print(len(name_dic))
    
    print('writing...')
    #saved in this pkl
    with open('name_url.pkl', 'wb') as f:
        pickle.dump(name_dic, f)
    
    return name_dic


# In[17]:

# In[9]:


#function to get the dictionary of {name:url}
#The result was saved in name_url_bykey.pkl, no need to run it
#https://www.the-numbers.com/movie/budgets/all/5501
#The structure of the dictionary is as following:
#{name of the movie: url(stirng),...}
def extract_url_dic_bykey():
    url='https://www.the-numbers.com/movies/keywords'
    name_dic={}
    host_url='https://www.the-numbers.com'
    page_response=requests.get(url)
    root=BeautifulSoup(page_response.content.decode('utf-8'), "html.parser")
    url_dic=dict()
    for tr in root.find_all('tr'):
        if len(tr.find_all('td'))>0:
            td=tr.find_all('td')[0]
            keyword=html.unescape(td.get_text()).replace(u'\xa0', u' ')
            url_dic[keyword]=host_url+td.a.get('href')
            
    #with open('key_url.pkl', 'wb') as f:
    #    pickle.dump(url_dic, f)

    for keyword,url in url_dic.items():
        subpage_response=requests.get(url)
        subroot=BeautifulSoup(subpage_response.content.decode('utf-8'), "html.parser")
        for tr in subroot.find_all('tr'):
            if len(tr.find_all('td'))>1:
                try:
                    year=html.unescape(tr.find_all('td')[0].get_text()).replace(u'\xa0', u' ').split('/')[2]
                except:
                    print(tr.find_all('td')[0].get_text())
                    continue
                td=tr.find_all('td')[1]
                name=html.unescape(td.get_text()).replace(u'\xa0', u' ')
                name_dic[name+'('+year+')']=host_url+td.a.get('href')
    
    with open('name_url_bykey.pkl', 'wb') as f:
        pickle.dump(name_dic, f)
    
    return name_dic


# In[31]:



# In[35]:


#get all the movie information and save in movie_info.pkl
#may run several hours
def get_all_movie_info():
    with open('name_url.pkl', 'rb') as f:
        name_dic = pickle.load(f)
    
    pool = Pool(processes=10)
    
    total_dic=dict()
    keys=list(name_dic.keys())
    pool_outputs = pool.map(get_info_with_name,keys)
    pool.close()
    pool.join()

    for i in range(len(keys)):
        total_dic[keys[i]]=pool_outputs[i]
    
    with open('movie_info.pkl', 'wb') as f:
        pickle.dump(total_dic, f)
    
    return total_dic




# In[11]:


#get all the movie categories information
#may run several hours
def get_all_movie_categories():
    movie_categories=dict()
    keyword, genre, prod, creat, company, country, cast =dict(), dict(), dict(), dict(), dict(), dict(), dict()
    franchise=dict()
    person_name_url=dict()
    
    
    with open('name_url.pkl', 'rb') as f:
        name_dic = pickle.load(f)
    
    for name, value in name_dic.items():
        summary_url=value['url']+"#tab=summary"
        #summary_url=value+"#tab=summary"
        summary_response = requests.get(summary_url, allow_redirects=False)
        if summary_response.status_code != 404:
            summary_dic = parse_page(summary_response.content, "summary")
            #print(summary_dic)
            print(name)
            if 'Genre' in summary_dic.keys():
                genre[summary_dic['Genre']]=genre.get(summary_dic['Genre'],[])+[name]
            if 'Creative Type' in summary_dic.keys():
                creat[summary_dic['Creative Type']]=creat.get(summary_dic['Creative Type'],[])+[name]
            if 'Production Method' in summary_dic.keys():
                for mt in summary_dic['Production Method']:
                    prod[mt]=prod.get(mt,[])+[name]
                    #print(prod.get(mt,[]))
            if 'Production Companies' in summary_dic.keys():
                for cp in summary_dic['Production Companies']:
                    company[cp]=company.get(cp,[])+[name]
            if 'Production Countries' in summary_dic.keys():
                for ct in summary_dic['Production Countries']:
                    country[ct]=country.get(ct,[])+[name]
            if 'Keywords' in summary_dic.keys():
                for keywords in summary_dic['Keywords']:
                    keyword[keywords]=keyword.get(keywords,[])+[name]
            if 'Franchise' in summary_dic.keys():
                franchise[summary_dic['Franchise']]=franchise.get(summary_dic['Franchise'],[])+[name]
                
        cast_url=value['url']+"#tab=cast-and-crew"
        #cast_url=value+"#tab=cast-and-crew"
        cast_response=requests.get(cast_url, allow_redirects=False)
        if cast_response.status_code !=404:
            cast_dic = parse_page(cast_response.content, "cast")
            if 'production' in cast_dic.keys():
                for person in cast_dic['production']:
                    person_name=person['name']
                    if person_name not in person_name_url.keys():
                        person_name_url[person_name]=person['url']
                    temp_dict={'role': person['role'],'name': name}
                    cast[person_name]=cast.get(person_name,[])+[temp_dict]
                    
            if 'leading_members' in cast_dic.keys():
                for person in cast_dic['leading_members']:
                    person_name=person['name']
                    if person_name not in person_name_url.keys():
                        person_name_url[person_name]=person['url']
                        
            if 'supporting_cast' in cast_dic.keys():
                for person in cast_dic['supporting_cast']:
                    person_name=person['name']
                    if person_name not in person_name_url.keys():
                        person_name_url[person_name]=person['url']
            
            if 'cameos' in cast_dic.keys():
                for person in cast_dic['cameos']:
                    person_name=person['name']
                    if person_name not in person_name_url.keys():
                        person_name_url[person_name]=person['url']
                        
            if 'uncategorized' in cast_dic.keys():
                for person in cast_dic['uncategorized']:
                    person_name=person['name']
                    if person_name not in person_name_url.keys():
                        person_name_url[person_name]=person['url']
                        
        #pprint(keyword)
        #pprint(genre)
        #pprint(prod)
        #pprint(creat)
        #pprint(company)
        #pprint(country)
        #pprint(cast)
        #pprint(franchise)
        
    movie_categories['Genre']=genre
    movie_categories['Creative Type']=creat
    movie_categories['Production Method']=prod
    movie_categories['Production Companies']=company
    movie_categories['Production Countries']=country
    movie_categories['Keywords']=keyword
    movie_categories['Franchise']=franchise
    movie_categories['cast']=cast
    
    print('Writing...')
    with open('movie_categories.pkl', 'wb') as f:
        pickle.dump(movie_categories, f)
        
    with open('person_name_url.pkl', 'wb') as f:
        pickle.dump(person_name_url, f)
        
    return movie_categories


# In[105]:

# In[12]:


def parse_person_page(html_page, title):
    root=BeautifulSoup(html_page.decode('utf-8'), "html.parser")
    lis=dict()
    if title=="summary":
        title_name=['', 'role', 'Movies', 'Domestic Box Office',  'International Box Office', 'Worldwide Box Office']
        lis['Career Summary']=center_table_helper(root, title_name, 'h2', 'Career Summary', 'person')
        
        title_name=['Record', 'Rank', 'Amount']
        #get the rank list
        lis['Latest Ranking']=center_table_helper(root, title_name, 'h2', 'Latest Ranking on Selected Box Office Record Lists')
        pass      
    
    elif title=="acting":
        title_name=['Release Date', 'Title', 'Role' ,' Domestic Box Office', 'International Box Office', 'Worldwide Box Office']
        lis['All Acting Credits']= center_table_helper(root, title_name, 'h2','All Acting Credits', 'person')
        
        title_name=['Release Date', 'Title', 'Opening Weekend Box Office', 'Max Theater Count', 'Domestic Box Office', 'Worldwide Box Office', 'Domestic Share']
        lis['Leading or Lead Ensemble Roles']=center_table_helper(root, title_name, 'h2', 'Leading or Lead Ensemble Roles','person')
        
        title_name=['Release Date', 'Title' ,'Opening Weekend Box Office', ' Max Theater Count', 'Domestic Box Office', 'Worldwide Box Office', 'Domestic Share']
        lis['Supporting Roles']=center_table_helper(root, title_name, 'h2', 'Supporting Roles', 'person')
        
        title_name=['Record', 'Rank', 'Amount']
        lis['Latest Ranking']=center_table_helper(root, title_name, 'h2', 'Latest Ranking on All Acting Box Office Record Lists', 'person')
        pass

    
    
    elif title=="technical":
        title_name=['Release Date', 'Title', 'Role' ,' Domestic Box Office', 'International Box Office', 'Worldwide Box Office']
        lis['All Technical Credits']= center_table_helper(root, title_name, 'h2','All Technical Credits', 'person')
        
        title_name=['Release Date', 'Title', 'Opening Weekend Box Office', 'Max Theater Count', 'Domestic Box Office', 'Worldwide Box Office', 'Domestic Share']
        lis['Director Credits']= center_table_helper(root, title_name, 'h2','Director Credits', 'person')
        
        title_name=['Release Date', 'Title', 'Opening Weekend Box Office', 'Max Theater Count', 'Domestic Box Office', 'Worldwide Box Office', 'Domestic Share']
        lis['Writer Credits']= center_table_helper(root, title_name, 'h2','Writer Credits', 'person')
        
        title_name=['Record', 'Rank', 'Amount']
        lis['Latest Ranking']= center_table_helper(root, title_name, 'h2','Latest Ranking on All Technical Box Office Record Lists','person')
        pass
    
    elif title=="news":
        host_url="https://www.the-numbers.com"
        url_list=list()
        for item in root.find_all('a'):
            if item.get_text().replace(u'\xa0', u' ')=='More...':
                url_list.append(host_url+item.get('href'))
                
        text_list=list()
        for url in url_list:
            url_response=requests.get(url)
            url_html=url_response.content
            url_root=BeautifulSoup(url_html.decode('utf-8'), "html.parser")
            for div in url_root.find_all('div'):
                if div.get('id')=='news':
                    news_content=html.unescape(div.get_text()).replace(u'\xa0', u' ').replace('\n',' ').replace('\r','')
                    text_list.append(news_content)
                    break

        lis['news']=text_list
        pass
    
    return lis


# ## PKL Explanation
# Currentlt, there are 5 pkl files.
# 
# * In name_url.pkl, there is a dictionary with the structure {name of movie: {'url': string, 'Release Date': datetime, 'Production Budget': int, 'Domestic Gross': int, 'Worldwide Gross': int},...}, where th key is the the movie name(year). Currently there are 5518 movies.
# 
# * In name_url_bykey.pkl, there is a dictionaey with the structure {movie name: url,...}, where the key is the movie name(year), the value is the url link to the page contains the information of the movie. Currently, there are 13458 movies, but not used. 
# 
# * In person_name_url.pkl, there is a dictionary with the structure {person name: url,...}, where the key is the user name and the value is the url link to the page contains the inforation of the user.
# 
# * In movie_categories.pkl, there is a dictionary with the movies name lists categoried with different tags. The details is explained in the api function get_movie_categories().
# 
# * in movie_info.pkl, there is a dictionary with the structure {movie name: information dictionary, ....}, where the information dictionary is the output of the get_info_with_name() function described as below.

# In[18]:


#get the movie information with the movie name(movie name+(year)), this one will get the newest data through http request
#The structure of the output is as following:
#   {'box_office': {'daliy': [{'Change':float, 
#                              'Date': datetime, 
#                              'Gross': int, 
#                              'Per Theater':int, 
#                              'Rank':int, 
#                              'Theaters':int,
#                              'Total Gross': int,
#                              'Week':int},... ],   
#                 'demostic': [{'Rank': int,
#                              'Record': string,
#                              'Revenue': int},...],
#                 'weekend': [{'Change': float,
#                             'Date': datetime,
#                             'Gross': int,
#                             'Per Theater': int,
#                             'Rank': int,
#                             'Theaters': int,
#                             'Total Gross': int,
#                             'Week': int},...],
#                 'weekly': [{'Change': float,
#                            'Date': datetime,
#                            'Gross': int,
#                            'Per Theater': int,
#                            'Rank': int,
#                            'Theaters': int,
#                            'Total Gross': int,
#                            'Week': int},...]},
#   'cast': {'cameos': [{'name': string,
#                      'url': string},...],
#            'leading_members': [{'name': string,
#                               'url': string},...],
#            'production': [{'name': string,
#                          'role': string,
#                          'url': string},...],
#            'supporting_cast': [{'name': string,
#                               'url': string},...],
#            'uncategorized': [{'name': string,
#                             'url': string},...]},
#   'international': {'Box Office Summary': [{'Maximum Theaters': int,
#                                           'Opening Weekend': int,
#                                           'Opening Weekend Theaters': int,
#                                           'Release Date': datetime,
#                                           'Report Date': datetime,
#                                           'Territory': sting,
#                                           'Theatrical Engagements': int,
#                                           'Total Box Office': int},...],
#                     'International Box Office': [{'Rank': int,
#                                                 'Record': string,
#                                                 'Revenue': int},...],
#                     'Worldwide Box Office': [{'Rank': int,
#                                             'Record': string,
#                                             'Revenue': int},...]},
#    'news': {'news': [string, ....]},
#    'summary': {'Budget': int,
#             'Creative Type': string,
#             'Domestic Releases': {'IMAX': datetime,        (may not have IMAX version)
#                                   'Wide': datetime},
#             'Franchise': string,
#             'Genre': string,
#             'International Releases': {location: {'Wide': datetime},...},   (may have IMAX version)
#             'Keywords':[string,...],
#             'MPAA Rating': string,
#             'Production Companies': [string,...],
#             'Production Countries': [string,...],
#             'Production Method': [string,...],
#             'Running Time': string,
#             'Source': string,
#             'Video Release': datetime,
#             'ranking on other records': [{'Amount': int,
#                                           'Chart Date': string,
#                                           'Days In Release': int,
#                                           'Rank': int,
#                                           'Record': string},...]}                 
#}
def get_info_with_name(name):
    with open('name_url.pkl', 'rb') as f:
        name_dic = pickle.load(f)
    print(name)
    
    name_info=get_info(name_dic[name]['url'])
    
    return name_info


# # The following is the api functions

# # First API

# In[25]:


#get the movie information with the movie name(movie name+(year)), this one will get the data from the local file which was scrapped from the internet before
#The structure of the output is as following:
#   {'box_office': {'daliy': [{'Change':float, 
#                              'Date': datetime, 
#                              'Gross': int, 
#                              'Per Theater':int, 
#                              'Rank':int, 
#                              'Theaters':int,
#                              'Total Gross': int,
#                              'Week':int},... ],   
#                 'demostic': [{'Rank': int,
#                              'Record': string,
#                              'Revenue': int},...],
#                 'weekend': [{'Change': float,
#                             'Date': datetime,
#                             'Gross': int,
#                             'Per Theater': int,
#                             'Rank': int,
#                             'Theaters': int,
#                             'Total Gross': int,
#                             'Week': int},...],
#                 'weekly': [{'Change': float,
#                            'Date': datetime,
#                            'Gross': int,
#                            'Per Theater': int,
#                            'Rank': int,
#                            'Theaters': int,
#                            'Total Gross': int,
#                            'Week': int},...]},
#   'cast': {'cameos': [{'name': string,
#                      'url': string},...],
#            'leading_members': [{'name': string,
#                               'url': string},...],
#            'production': [{'name': string,
#                          'role': string,
#                          'url': string},...],
#            'supporting_cast': [{'name': string,
#                               'url': string},...],
#            'uncategorized': [{'name': string,
#                             'url': string},...]},
#   'international': {'Box Office Summary': [{'Maximum Theaters': int,
#                                           'Opening Weekend': int,
#                                           'Opening Weekend Theaters': int,
#                                           'Release Date': datetime,
#                                           'Report Date': datetime,
#                                           'Territory': sting,
#                                           'Theatrical Engagements': int,
#                                           'Total Box Office': int},...],
#                     'International Box Office': [{'Rank': int,
#                                                 'Record': string,
#                                                 'Revenue': int},...],
#                     'Worldwide Box Office': [{'Rank': int,
#                                             'Record': string,
#                                             'Revenue': int},...]},
#    'news': {'news': [string, ....]},
#    'summary': {'Budget': int,
#             'Creative Type': string,
#             'Domestic Releases': {'IMAX': datetime,        (may not have IMAX version)
#                                   'Wide': datetime},
#             'Franchise': string,
#             'Genre': string,
#             'International Releases': {location: {'Wide': datetime},...},   (may have IMAX version)
#             'Keywords':[string,...],
#             'MPAA Rating': string,
#             'Production Companies': [string,...],
#             'Production Countries': [string,...],
#             'Production Method': [string,...],
#             'Running Time': string,
#             'Source': string,
#             'Video Release': datetime,
#             'ranking on other records': [{'Amount': int,
#                                           'Chart Date': string,
#                                           'Days In Release': int,
#                                           'Rank': int,
#                                           'Record': string},...]}                 
#}
def get_info_with_localname(name):
    with open('movie_info.pkl', 'rb') as f:
        name_dic = pickle.load(f)
    
    return name_dic[name]


# In[26]:


# In[14]:


#get all the list of categories
#The structure of the output is as following:
#{ 'Genre': {keyword(genre name): [string(movie name),...],...},
#  'Creative Type': {keyword(type name): [string(movie name),...],...},
#  'Production Method':{keyword(method name): [string(movie name),...],...},
#  'Production Companies':{keyword(company name): [string(movie name),...],...},
#  'Production Countries':{keyword(country name): [string(movie name),...],...},
#  'Franchise':{keyword(franchise name): [string(movie name),...],...},
#  'Keywords':{keyword(keyword name): [string(movie name),...],...},
#  'cast':{keyword(actor name): [string(movie name),...],...},
#}
def get_movie_categories():
    with open('movie_categories.pkl', 'rb') as f:
        test_categories = pickle.load(f)
    
    return test_categories


# In[14]:


# # Third API

# In[15]:


#given the name of the actor/writor/director/..., return the information dictionary
#The structure of the output is as following:
#{'acting': {'All Acting Credits': [{' Domestic Box Office': int,
#                                    'International Box Office': int,
#                                    'Release Date': datetime,
#                                    'Role': string,
#                                    'Title': string,
#                                    'Worldwide Box Office': int},...],
#            'Latest Ranking': [{'Amount': int,
#                                'Rank': int,
#                                'Record': string},...],
#            'Leading or Lead Ensemble Roles': [{'Domestic Box Office': int,
#                                                'Domestic Share': string,
#                                                'Max Theater Count': int,
#                                                'Opening Weekend Box Office': int,
#                                                'Release Date': datetime,
#                                                'Title': string,
#                                                'Worldwide Box Office': int},...],
#             'Supporting Roles': [{' Max Theater Count': int,
#                                  'Domestic Box Office': int,
#                                  'Domestic Share': float,
#                                  'Opening Weekend Box Office': int,
#                                  'Release Date': datetime,
#                                  'Title': string,
#                                  'Worldwide Box Office': int},...]}
#  'news': {'news': [string, ...]}
#  'summary': {'Career Summary': [{'Domestic Box Office': int,
#                                'International Box Office': int,
#                                 'Movies': int,
#                                 'Worldwide Box Office': int,
#                                 'role': string},...],
#               'Latest Ranking': [{'Amount': int,
#                                'Rank': int,
#                                 'Record': string},...]}
#   'technique': {'All Technical Credits': [{' Domestic Box Office': int,
#                                          'International Box Office': int,
#                                          'Release Date': datetime,
#                                          'Role': string,
#                                          'Title': string,
#                                          'Worldwide Box Office': int},...],
#               'Director Credits': [{'Domestic Box Office': int,
#                        'Domestic Share': float,
#                        'Max Theater Count': int,
#                        'Opening Weekend Box Office': int,
#                        'Release Date': datetime,
#                        'Title': string,
#                        'Worldwide Box Office': int},...]
#               'Latest Ranking': [{'Amount': int,
#                       'Rank': int,
#                       'Record': string},...]}
#}
#
def get_info_by_person_name(name):
    with open('person_name_url.pkl', 'rb') as f:
        person_name_url = pickle.load(f)
    
    if name not in person_name_url.keys():
        return None
    
    url=person_name_url[name]
    #print(url)
    summary_url=url+"#tab=summary"
    news_url=url+"#tab=news"
    acting_url=url+"#tab=acting"
    technical_url=url+"#tab=technical"
    
    summary_response = requests.get(summary_url)
    news_response = requests.get(news_url)
    acting_response = requests.get(acting_url)
    technical_response = requests.get(technical_url)
    
    summary_dic, news_dic, acting_dic,technical_dic = dict(), dict(), dict(), dict()
    
    if summary_response.status_code != 404:
        summary_dic = parse_person_page(summary_response.content, "summary")
        #pprint(summary_dic) 
    
    if news_response.status_code != 404:
        news_dic = parse_person_page(news_response.content, "news")
        #pprint(summary_dic) 
        
    if acting_response.status_code != 404:
        acting_dic = parse_person_page(acting_response.content, "acting")
        #pprint(acting_dic) 
        
    if technical_response.status_code != 404:
        technical_dic = parse_person_page(technical_response.content, "technical")
        #pprint(technical_dic) 
        
    total_dic=dict()
    total_dic['summary']=summary_dic
    total_dic['news']=news_dic
    total_dic['acting']=acting_dic
    total_dic['technique']=technical_dic
    
    return total_dic


# In[51]:


