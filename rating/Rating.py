
# coding: utf-8

# In[6]:


import pickle
from multiprocessing import Pool
import pandas as pd

def get_movie_names_all():
    with open('movie_info.pkl', 'rb') as f:
        movie_infos = pickle.load(f)
    count = 0
    movie_names = list(movie_infos.keys())
    return movie_names

#movies_names = get_movie_names_all()


# ## IMDB

# In[2]:


def get_match_names(movies_names):
    new_names =  list(movies_names)

    for i in range(len(new_names)):
        index = new_names[i].rindex('(') 
        new_names[i] = new_names[i][:index]
        new_names[i] = new_names[i].replace("’", "'")
        new_names[i] = new_names[i].replace('—',' - ')

    # manual rectification
    new_names[3] = 'Star Wars: The Force Awakens'
    new_names[64] = 'A Christmas Carol'
    new_names[152] = 'Mission: Impossible - Rogue Nation '
    new_names[279] = 'Star Wars: Episode I - The Phantom Menace'
    new_names[280] = 'Star Wars: Episode III - Revenge of the Sith'
    new_names[281] = 'Star Wars: Episode II - Attack of the Clones'
    new_names[296] = 'Insurgent'
    new_names[308] = 'Allegiant'
    new_names[346] = 'A Series of Unfortunate Events'
    new_names[567] = 'Arthur and the Invisibles'
    new_names[679] = 'Wall Street: Money Never Sleeps'
    new_names[716] = 'The Lorax'
    new_names[772] = 'Dragon Blade'
    new_names[926] = 'Monster Hunt'
    new_names[953] = "Mr. Popper's Penguins"
    new_names[1022]= 'Barnyard'
    new_names[1045] = 'Planes'
    new_names[1057] = 'Garfield'
    new_names[1253] = 'Curse of the Golden Flower'
    new_names[1269] = 'Unleashed'
    new_names[1314] = 'Spy Kids 3: Game Over'
    new_names[1472] = 'The Grandmaster'
    new_names[1480] = 'Mousehunt'
    new_names[1521] = 'Dark Planet'
    new_names[1536] = 'Ip Man 3'
    new_names[1578] = 'Underworld: Rise of the Lycans'
    new_names[1662] = 'The Horseman on the Roof'
    new_names[1674] = 'Ponyo'
    new_names[1694] = 'Star Wars: Episode VI - Return of the Jedi'
    new_names[1896] = '1911'
    new_names[1902] = 'The Color of Freedom'
    new_names[1903] = "A Warrior's Tail"
    new_names[1922] = 'Che, Part 1'
    new_names[1967] = 'Ghosts of Mars'
    new_names[1984] = 'Divine Secrets of the Ya-Ya Sisterhood'
    new_names[2044] = 'Snow White: A Tale of Terror'
    new_names[2048] = 'A Madea Christmas'
    new_names[2169] = 'Lords of Dogtown'
    new_names[2201] = 'Little White Lies'
    new_names[2203] = 'Kung Fu Killer'
    new_names[2204] = "A Turtle's Tale: Sammy's Adventures"
    new_names[2205] = 'Space Dogs'
    new_names[2241] = "Howl's Moving Castle"
    new_names[2247] = 'Star Wars: Episode V - The Empire Strikes Back'
    new_names[2259] = 'The Secret World of Arrietty'
    new_names[2264] = 'Jaws: The Revenge'
    new_names[2272] = 'Coco Before Chanel'
    new_names[2329] = 'Underdogs'
    new_names[2380] = 'Boo! A Madea Halloween'
    new_names[2385] = "Madea's Witness Protection"
    new_names[2400] = 'Boo 2! A Madea Halloween'
    new_names[2454] = 'Two for the Money'
    new_names[2549] = 'Princess Mononoke '
    new_names[2573] = 'Alex Koltchak'
    new_names[2579] = 'Shattered'
    new_names[2585] = 'The Baader Meinhof Complex'
    new_names[2587] = 'Rust and Bone'
    new_names[2601] = 'Thirteen Ghosts'
    new_names[2611] = 'Spirited Away'
    new_names[2620] = 'Land of the Dead'
    new_names[2687] = '9½ Weeks'
    new_names[2704] = 'The White Ribbon '
    new_names[2742] = 'Hero'
    new_names[2760] = 'They'
    new_names[2771] = 'The Illusionist'
    new_names[2777] = 'Mune: Guardian of the Moon'
    new_names[2778] = 'Dragon Hunters'
    new_names[2789] = 'Arn: The Knight Templar'
    new_names[2801] = 'Pan’s Labyrinth'
    new_names[2837] = 'Welcome to the Sticks'
    new_names[2864] = 'Bad Grandpa'
    new_names[2977] = 'Three Burials'
    new_names[2991] = 'District B13'
    new_names[3066] = 'The Diving Bell and the Butterfly'
    new_names[3078] = 'Wild Grass'
    new_names[3147] = 'The Widow of Saint-Pierre'
    new_names[3172] = 'The Boy in the Striped Pajamas'
    new_names[3182] = 'Tae Guk Gi: The Brotherhood of War'
    new_names[3185] = 'Ernest & Celestine'
    new_names[3243] = 'How to Be a Player'
    new_names[3287] = 'A Woman, a Gun and a Noodle Shop'
    new_names[3290] = 'City of Life and Death'
    new_names[3295] = 'Legend of Kung Fu Rabbit'
    new_names[3298] = 'Space Battleship Yamato'
    new_names[3301] = 'A Tale of Three Cities'
    new_names[3304] = 'Maadadayo'
    new_names[3310] = 'Star Wars: Episode IV - A New Hope'
    new_names[3359] = 'Machine Gun McCain'
    new_names[3438] = 'Mafia!'
    new_names[3467] = 'The Red Violin'
    new_names[3492] = 'I Am Love'
    new_names[3530] = 'The Chambermaid on the Titanic'
    new_names[3540] = 'The Good the Bad the Weird'
    new_names[3541] = 'Police Academy: Mission to Moscow'
    new_names[3550] = 'Of Horses and Men'
    new_names[3588] = 'Loose Cannons'
    new_names[3628] = 'Two Evil Eyes'
    new_names[3630] = 'The Girl on the Train'
    new_names[3632] = 'Red Riding: The Year of Our Lord 1974'
    new_names[3633] = 'Flame & Citron'
    new_names[3640] = 'The Haunting in Connecticut 2: Ghosts of Georgia'
    new_names[3656] = 'Shipwrecked'
    new_names[3673] = 'Valley of the Wolves: Iraq'
    new_names[3699] = 'New Nightmare'
    new_names[3709] = 'The Boondock Saints II: All Saints Day'
    new_names[3722] = '8 Women'
    new_names[3726] = 'When Did You Last See Your Father?'
    new_names[3746] = 'Battle Ground 625'
    new_names[3747] = 'My Lucky Star'
    new_names[3748] = 'Top Cat Begins'
    new_names[3753] = 'Chirstmas in Beverly Hills'
    new_names[3754] = 'Mr. Church'
    new_names[3760] = 'Far from Men'
    new_names[3777] = 'Alias Betty'
    new_names[3779] = 'Borg vs McEnroe'
    new_names[3789] = 'The Wave'
    new_names[3863] = 'Hard to Be a God'
    new_names[3872] = 'Adventures in Appletown'
    new_names[3888] = 'Hannah Montana and Miley Cyrus: Best of Both Worlds Concert'
    new_names[3931] = 'Van Wilder: Party Liaison'
    new_names[3973] = 'The Great Train Robbery'
    new_names[4000] = 'The Protector'
    new_names[4031] = 'Tao Jun Jie'
    new_names[4116] = 'The Barbarian Invasions'
    new_names[4124] = 'Once Upon a Time in the West'
    new_names[4184] = 'Navy Seals vs. Zombies'
    new_names[4206] = 'The Names of Love'
    new_names[4225] = 'Saving Private Perez'
    new_names[4227] = "Mozart's Sister"
    new_names[4230] = 'Lady Vengeance'
    new_names[4233] = 'Lilya 4-Ever'
    new_names[4236] = 'Exiled'
    new_names[4256] = 'Survival of the Dead'
    new_names[4320] = 'Polina'
    new_names[4322] = 'Buen Día, Ramón'
    new_names[4330] = 'Futuro Beach'
    new_names[4336] = 'The Geographer Drank His Globe Away'
    new_names[4357] = 'Heavy Trip '
    new_names[4359] = 'House of Sand'
    new_names[4388] = 'The Secret in Their Eyes'
    new_names[4394] = 'Trollhunter'
    new_names[4407] = 'In the Name of the King: The Last Job'
    new_names[4412] = 'March of the Penguins'
    new_names[4422] = 'City of God'
    new_names[4452] = "A Nightmare on Elm Street 2: Freddy's Revenge"
    new_names[4518] = 'Summer Storm'
    new_names[4557] = 'Beer League'
    new_names[4564] = 'Journey to Saturn'
    new_names[4570] = 'Friday the 13th: The Final Chapter'
    new_names[4577] = 'Silver Medallist'
    new_names[4604] = "Valley of the Heart's Delight"
    new_names[4656] = 'The Road Warrior'
    new_names[4665] = 'Das Leben der Anderen'
    new_names[4671] = 'The Triplets of Belleville'
    new_names[4712] = 'Hum To Mohabbat Karega'
    new_names[4733] = 'Vampire Killers'
    new_names[4738] = 'Sinatra Being Frank'
    new_names[4781] = 'El crimen del padre Amaro'
    new_names[4784] = 'The Greatest Movie Ever Sold'
    new_names[4792] = "A Beginner's Guide to Snuff"
    new_names[4793] = 'Run Lola Run'
    new_names[4798] = 'Under the Same Moon'
    new_names[4803] = 'Son of Saul'
    new_names[4812] = 'Caramel'
    new_names[4839] = 'Nueve Reinas'
    new_names[4867] = 'Girl House'
    new_names[4878] = 'Queen of the Mountains'
    new_names[4894] = 'The Amazing Catfish'
    new_names[4914] = 'The Good, the Bad and the Ugly'
    new_names[4923] = 'The Second Mother'
    new_names[4929] = 'The Knife of Don Juan'
    new_names[4944] = 'The Raid: Redemption'
    new_names[4955] = 'The Dead Undead'
    new_names[5024] = 'A Lego Brickumentary'
    new_names[5083] = '4 Months, 3 Weeks and 2 Days'
    new_names[5089] = 'Elza'
    new_names[5102] = 'A Separation'
    new_names[5107] = 'Live-In Maid'
    new_names[5122] = 'The Conformist'
    new_names[5189] = 'Seven Samurai'
    new_names[5195] = 'Boy and the World'
    new_names[5220] = 'The King of Najayo'
    new_names[5226] = 'Bizarre'
    new_names[5237] = 'Censored Voices'
    new_names[5258] = 'Cries & Whispers'
    new_names[5277] = 'Dogtooth'
    new_names[5354] = 'Fistful of Dollars'
    new_names[5362] = 'The Business of Fancydancing'
    new_names[5381] = 'Children of Heaven'
    new_names[5390] = 'The World Is Mine'
    new_names[5393] = "Sweet Sweetback's Baadasssss Song"
    new_names[5432] = 'Lunch Time Heroes'
    return new_names

#new_names = get_match_names(movies_names)
# In[98]:


def getdata(data):
    if data == 'N/A':
        return None
    if data.find('%') != -1:
        data = data[:-1]
    if data.find('.') != -1:
        return float(data)
    else:
        return int(data)
    
def getRotTmt(data):
    for record in data:
        if record['Source'] == 'Rotten Tomatoes':
            return int(record['Value'][:-1])
    return None
            

def search_rating_via_IMDB(formal_names, names):
    parameters = {'i':'tt3896198',
                  'apikey':'22f49a17',
                  'plot': 'full'} #cff99532
    queryURL = "http://www.omdbapi.com/"
    
    separator = '?'
    
    for i in parameters:
        queryURL = queryURL+separator+i+"="+parameters[i]
        separator = '&'

    results = []
    movie_rating = pd.DataFrame(columns=['name', 'imdbRating','Rotten_Tomatoes','Metacritic','imdbVotes','plot'])
    
    name = []
    imdbRating = []
    Rotten_Tomatoes = []
    Metacritic = []
    imdbVotes = []
    notfound = []
    plot = []
    
    index = 0
    for i in range(0, len(formal_names)):
        movie = names[i]
        name.append(formal_names[i])
        qword = re.sub(r' ', r'%20', movie).strip()
        query = queryURL + separator + "t=" + qword
    
      
        try:
            data = json.load(urllib2.urlopen(query))
            if data['Response'] == 'False':
                query = queryURL + separator + "t=" + qword.replace("and", "&")
                data = json.load(urllib2.urlopen(query))
                if data['Response'] == 'False':
                    idx = qword.find(':')
                    query = queryURL + separator + "t=" + qword[:idx]
                    data = json.load(urllib2.urlopen(query))
                    if data['Response'] == 'False':
                        idx = qword.find('(')
                        query = queryURL + separator + "t=" + qword[:idx]
                        data = json.load(urllib2.urlopen(query))
                        if data['Response'] == 'False':
                            print(str(i) +"  "+ movie)
                            Metacritic.append(None)
                            imdbRating.append(None)
                            Rotten_Tomatoes.append(None)
                            imdbVotes.append(None)
                            plot.append(None)
                            notfound.append(formal_names[i])
                            continue 

            Metacritic.append(getdata(data['Metascore']))
            imdbRating.append(getdata(data['imdbRating']))
            Rotten_Tomatoes.append(getRotTmt(data['Ratings']))
            imdbVotes.append(getdata(data['imdbVotes'].replace(',','')))
            plot.append(data['Plot'])
            
        except:
            Metacritic.append(None)
            imdbRating.append(None)
            Rotten_Tomatoes.append(None)
            imdbVotes.append(None)
            plot.append(None)
            notfound.append(formal_names[i])
                    
        index += 1
    
    movie_rating.loc[:,'name'] = name
    movie_rating.loc[:,'imdbRating'] = imdbRating
    movie_rating.loc[:,'Rotten_Tomatoes'] = Rotten_Tomatoes
    movie_rating.loc[:,'Metacritic'] = Metacritic
    movie_rating.loc[:,'imdbVotes'] = imdbVotes
    movie_rating.loc[:,'plot'] = plot
    
    movie_rating.set_index('name', inplace=True)
    
    movie_rating.to_csv('ratings.csv')
    
    file = open('notfound_movie.txt', 'w')
    for item in notfound:
        file.write("%s\n" % item)
    file.close()

    return movie_rating, notfound
    
    
#movie_rating,notfound = search_rating_via_IMDB(movies_names, new_names)


# # In[99]:


# print(movie_rating)
# print(notfound)
# print(len(notfound))

