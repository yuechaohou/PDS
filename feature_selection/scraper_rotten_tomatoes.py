
# coding: utf-8

# In[6]:


# setup library imports
import io, time, json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.rottentomatoes.com/m/"


# In[7]:


def retrieve_html(url):
    """
    Return the raw HTML at the specified URL.

    Args:
        url (string): 

    Returns:
        status_code (integer):
        raw_html (string): the raw HTML content of the response, properly encoded according to the HTTP headers.
    """
    
    # Write solution here
    # pass
    response = requests.get(url)
    return response.status_code, response.text

# AUTOLAB_IGNORE_START
# result = retrieve_html("http://www.nytimes.com/2016/08/28/magazine/inside-facebooks-totally-insane-unintentionally-gigantic-hyperpartisan-political-media-machine.html")
result = retrieve_html("https://www.rottentomatoes.com/m/rampage_2018")
# print(result)
# AUTOLAB_IGNORE_STOP


# In[17]:


def get_rating(movie_name, BASE_URL=BASE_URL):
    url = BASE_URL + movie_name
    code, html = retrieve_html(url)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    tomatometer = soup.find('span', {'class' : 'meter-value superPageFontColor'})
    value_span = tomatometer.find('span')
    
    rating = float(value_span.text) / 100
    return rating
    
    
movie_name = "rampage_2018"

rating = get_rating(movie_name, BASE_URL)


# In[48]:


def get_critic_reviews(movie_name, BASE_URL=BASE_URL):
    url_next = BASE_URL + movie_name + "/reviews"
    code, html = retrieve_html(url_next)
    
    reviews = []
    
    flag = True
    soup = BeautifulSoup(html, 'html.parser')
    count = soup.find('span', {'class' : 'pageInfo'}).text
    count = int(count.split(" ")[3])
    print(count)
    
    for i in range(count):
        print("new loop")
        review_containers = soup.findAll('div', {'class' : 'review_container'})
        
        for review_container in review_containers:
            label = review_container.div['class'][3]
            if label == 'rotten':
                label = 0 # negative review
            else:
                label = 1 # positive review
            review = review_container.find('div', {'class' : 'the_review'}).text
            reviews.append({'rating':label, 'review':review})
            
        url_next = soup.findAll('a', {'class' : 'btn btn-xs btn-primary-rt'})[1]['href']
        # print(soup.find('a', {'class' : 'btn btn-xs btn-primary-rt'}))
        url_next = 'https://www.rottentomatoes.com' + url_next
        print(url_next)
        # print(soup.findAll('a', {'class' : 'btn btn-xs btn-primary-rt'}))
        code, html = retrieve_html(url_next)
    
    return reviews
    
get_critic_reviews(movie_name)
    


# In[4]:


def parse_page(html):
    """
    Parse the reviews on a single page of a movie.
    
    Args:
        html (string): String of HTML corresponding to a rottan tomatoes restaurant

    Returns:
        tuple(list, string): a tuple of two elements
            ratings: list of dictionaries corresponding to the extracted review information
            reviews: URL for the next page of reviews (or None if it is the last page)
    """
    
    # Write solution here
    # pass
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []
    nextURL = None
    
    nextPage = soup.find('a', {'class' : 'u-decoration-none next pagination-links_anchor'})
    if nextPage is not None:
        nextURL = nextPage['href']
    
    ['href']
    reviews_with_sidebar = soup.findAll('div', {'class' : 'review review--with-sidebar'})
    for review_block in reviews_with_sidebar:
        review_id = review_block['data-review-id']
        user_id = review_block['data-signup-object'][8:]
        review_content = review_block.find('div', {'class' : 'review-wrapper'}).find('div', {'class' : 'review-content'})
        text = review_content.p.text
        rating = float((review_content.div.div.div['title']).split(' ')[0])
        # date = review_content.div.span.string.strip()
        date = str(review_content.div.span.string).strip()
        review = {}
        review['review_id'] = review_id
        review['user_id'] = user_id
        review['rating'] = rating
        review['date'] = date
        review['text'] = text
        reviews.append(review)
    
    #review_content = review_wrapper.find('div', {'class' : 'review-content'})
    return reviews, nextURL
    # review_list = soup.findAll('script', {'type' : 'application/ld+json'})
    # print(review_list[1])
    
# AUTOLAB_IGNORE_START

code, html = retrieve_html("https://www.rottentomatoes.com/m/rampage_2018/reviews/")
print(code)
#print(html)
parse_page(html)
# AUTOLAB_IGNORE_END


# ---

# ## Q 3.5: Extract all of the Yelp reviews for a Single Restaurant
# 
# So now that we have parsed a single page, and figured out a method to go from one page to the next we are ready to combine these two techniques and actually crawl through web pages! 
# 
# Using `requests`, programmatically retrieve __ALL__ of the reviews for a __single__ restaurant (provided as a parameter). Just like the API was paginated, the HTML paginates its reviews (it would be a very long web page to show 300 reviews on a single page) and to get all the reviews you will need to parse and traverse the HTML. As input your function will receive a URL corresponding to a Yelp restaurant. As output return a list of dictionaries (structured the same as question 3) containing the relevant information from the reviews.
# 
# ```python
# >>> data = extract_reviews('https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh')
# >>> print len(data)
# 513
# >>> print data[0]
# {
#     'text': "I've only had the pizza at the Porch, so this 4 stars is for the pizza! This is a great place to come, especially for their late-night half-off pizza special during the weekdays. I've looked at their non-pizza menu and it's a bit pricey, but from what other people tell me, the other food is great. The pizza is more than large enough to feed one person, but my friends and I usually split a couple between us so we can have different flavors. My favorites is the Piggie Pie, but I also had another seasonal pizza with goat cheese and fig on it, which was also extremely good! The crust is nice and crunchy on the outside, but soft enough on the inside, and the ratio of sauce-to-crust is perfect. Overall, this is a fabulous spot to come to if you're a student in Oakland looking for a late-night snack, or a non-student who wants a classier spot to eat at in Oakland. Will be back again!", 
#     'date': '12/22/2017', 
#     'user_id': 'SoItWLyIQUKtp8_SvQRMFg', 
#     'review_id': '5-Qhk9s94w7eHICF2Fhk7Q', 
#     'rating': 4.0
# }
# ```

# In[8]:


def extract_reviews(url):
    """
    Retrieve ALL of the reviews for a single restaurant on Yelp.

    Parameters:
        url (string): Yelp URL corresponding to the restaurant of interest.

    Returns:
        reviews (list): list of dictionaries containing extracted review information
    """
    # Write solution here
    # pass
    reviews = []
    while url is not None:
        code, html = retrieve_html(url)
        tempReviews, url = parse_page(str(html))
        reviews.extend(tempReviews)
    
    return reviews

#AUTOLAB_IGNORE_START
#extract_reviews('https://www.yelp.com/biz/piccolo-petes-cafe-san-francisco?page_src=best_of_yelp')
# AUTOLAB_IGNORE_END

