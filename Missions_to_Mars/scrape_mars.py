# Dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pandas as pd

def init_browser():
    executable_path = {'executable_path': 'chromedriver'}
    return Browser('chrome', **executable_path, headless=False)
def scrape():
    browser=init_browser()
    mars_dict={}
    ### NASA Mars News

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html=browser.html
    soup=bs(html,'html.parser')

    # Retrieve the latest news title
    news_title=soup.find_all('div', class_='content_title')[0].text
    # Retrieve the latest news paragraph
    news_p=soup.find_all('div', class_='rollover_description_inner')[0].text
    
    ### JPL Mars Space Images - Featured Image

    jpl_url="https://www.jpl.nasa.gov"
    jpl_image_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_image_url)

    # HTML object
    html=browser.html
    # Parse HTML
    soup=bs(html,"html.parser")
    # Retrieve image url
    image_url=soup.find_all('article')

    image_url=soup.find('article')['style']
    image_url=image_url.split("'")[1]

    featured_image_url=jpl_url+image_url
    

    ### Mars Weather

    # Scrape Mars weather from twitter
    url='https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html=browser.html
    soup=bs(html,'html.parser')

    # Retrieve the latest tweet from Mars weather twitter
    mars_weather=soup.find_all('p',class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')[0].text
    

    ### Mars Fact

    # Scrape Mars facts from https://space-facts.com/mars/
    url='https://space-facts.com/mars/'
    tables=pd.read_html(url)
    
    mars_fact=tables[0]
    mars_fact=mars_fact.rename(columns={0:"Profile",1:"Value"},errors="raise")
    mars_fact.set_index("Profile",inplace=True)
    mars_fact
    
    fact_table=mars_fact.to_html()
    fact_table.replace('\n','')
    
    ### Mars Hemispheres

    # Scrape Mars hemisphere title and image
    usgs_url='https://astrogeology.usgs.gov'
    url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html=browser.html
    soup=bs(html,'html.parser')

    # Extract hemispheres item elements
    mars_hems=soup.find('div',class_='collapsible results')
    mars_item=mars_hems.find_all('div',class_='item')
    hemisphere_image_urls=[]

    # Loop through each hemisphere item
    for item in mars_item:
        # Error handling
        try:
            # Extract title
            hem=item.find('div',class_='description')
            title=hem.h3.text
            # Extract image url
            hem_url=hem.a['href']
            browser.visit(usgs_url+hem_url)
            html=browser.html
            soup=bs(html,'html.parser')
            image_src=soup.find('li').a['href']
            if (title and image_src):
                # Print results
                print('-'*50)
                print(title)
                print(image_src)
            # Create dictionary for title and url
            hem_dict={
                'title':title,
                'image_url':image_src
            }
            hemisphere_image_urls.append(hem_dict)
        except Exception as e:
            print(e)

    # Create dictionary for all info scraped from sources above
    mars_dict={
        "news_title":news_title,
        "news_p":news_p,
        "featured_image_url":featured_image_url,
        "mars_weather":mars_weather,
        "fact_table":fact_table,
        "hemisphere_images":hemisphere_image_urls
    }
    # Close the browser after scraping
    browser.quit()
    return mars_dict