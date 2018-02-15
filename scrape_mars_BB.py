# coding: utf-8
# Dependencies
import pymongo
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
import time
# set mongo connection
#conn = 'mongodb://127.0.0.1:27017'
#client = pymongo.MongoClient(conn)

def init_browser():
    executable_path = {'executable_path':'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)
# setup scrape function
def scrape():
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    # target html parent
    results = soup.body.find_all('div', class_='content_title')
    # blank list to hold data
    titles = []
    # populate list
    for result in results:
        # Error handling
        try:
            title = result.find('a').text
            t = title.strip('\n')
            titles.append(t)
        except Exception as e:
            print(e)
    # identify most recent title as first in list
    target_title = titles[0]
    # target next html element containing teaser paragraph
    tease = soup.find('div', class_='rollover_description_inner').text
    # clean tease text
    teaser = tease.replace('\n', '')
    # next URL of page to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    # target html parent
    results = soup.body.find_all('article', class_='carousel_item')
    # clean html via string manipulation
    pic_loc = soup.article['style']
    pic_link = pic_loc.split(' ')[1].rstrip(';')
    clean_link = pic_link[5:57]
    # combine clean link with root to get full link
    root_url = 'https://www.jpl.nasa.gov'
    full_pic_link = root_url + clean_link
    # next URL of page to be scraped
    url = 'https://twitter.com/marswxreport?lang=en'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')
    # target html parent
    results = soup.body.find('div', class_='js-tweet-text-container')
    # identify weather report text
    mars_weather = results.find('p', class_='TweetTextSize').text
    # set URL and use pandas table reader to scrape tables
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    # identify target table
    facts_df = tables[0]
    # set target table columns and reset index
    facts_df.columns = ['Desc.', 'Value']
    facts_df.set_index('Desc.', inplace=True)
    # convert df to html table and replace line breaks
    #facts_tb = facts_df.to_html()
    facts = facts_df.to_html()
    #facts = facts_tb.replace('\n', '')
    # setup for multi-page image scrape
    browser = init_browser()    
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # create blank list
    hemisphere_image_urls = []
    # identify target image and title elements
    for i in range(1, 5):
        browser.click_link_by_partial_text(' Hemisphere Enhanced')
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        image = soup.find('a', target='_blank')
        title = soup.find('h2', class_='title').text
        title_img = {}
        #for item in image:   
        images = str(image).split('=')[1]
        images = images[1:-8]
        #root = 'https://astrogeology.usgs.gov'
        #link = root + images
        title_img['title'] = title
        title_img['link']= images
        hemisphere_image_urls.append(title_img)
        time.sleep(2)
    # setup consolidated dictionary for mongodb
    mars_data = {}
    # populate mars data dictionary with scraped items
    mars_data['news_title'] = target_title
    mars_data['news_teaser'] = teaser
    mars_data['feature_pic'] = full_pic_link
    mars_data['weather'] = mars_weather
    mars_data['hem_pics'] = hemisphere_image_urls
    mars_data['mars_facts'] = facts
    return mars_data
    