################################################################################
###
### date creation: 2023-03-06
### author: Alexander Busch (busch@iza.org)
### project: strike tracker (with coauthors)
###
###
### this file: 
###   - scrapes website-links of current press releases of trade unions
###   - mostly uses RSS-feeds for a quick and efficient process
###
################################################################################

# to do: 
# - safe one copy of current daily data & a merged version with historic data
# - add a running number for the day? 
# - integrate "vintage"/individual URLS and IGM-NRW: currently 22 websites not scraped! 
# - integrate DATES of url2 and igm main website 
# - automate on server 
# - add automated e-mail if there is an error message

import numpy as np
import random
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone    
import pickle
import sys
import time
from dateutil.parser import parse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.backends.backend_pdf
import csv
from apscheduler.schedulers.blocking import BlockingScheduler
mport schedule
import datetime
import pytz

# setup 
#pd.set_option('display.max_rows', 300)

# trigger start 
#def job():
#    tz = pytz.timezone('Europe/Berlin') # set up timezone
#    current_time = datetime.datetime.now(tz) 
#    if current_time.hour == 6: # check if 6 AM
      # code needs to be placed below

# set up schedule to run job every day at 6 AM Berlin time
#schedule.every().day.at("06:00").do(job)

# loop to continuously run the schedule
#while True:
#    schedule.run_pending()
#    time.sleep(1)


# read in links
union_data_rss = pd.read_excel("union_data.xlsx", sheet_name="rss", index_col=0)
union_data_rss["RSS-URL"] = union_data_rss["RSS-URL"].replace([np.nan, np.inf, -np.inf], "placeholder") # replace empty values
union_data_rss.replace({np.nan: "placeholder", np.inf: "placeholder", -np.inf: "placeholder"}, inplace=True) 
union_data_rss["RSS"].value_counts() # summary stats on websites used
union_data_rss["U-URL-Type"].value_counts() # summary stats

# save links: RSS
time_1 = time.time()
data_sites = []
for row in union_data_rss.index: 
  # current time
  germany = timezone("Europe/Berlin")
  time_now = str(datetime.now(germany))
  # continue loop if no RSS feed 
  url = union_data_rss["RSS-URL"][row]
  url_stub = re.findall(r"^https:\/\/([a-z-_.]+\.de)\/", url)
  if url != "placeholder":
    #print(url)
    r = requests.get(url)
    sleep(5)
    soup = BeautifulSoup(r.content, features='xml')
    sleep(5)
    #print(soup)
    articles = soup.findAll("item")
    for article in articles: 
      title = article.find("title", class_=False)
      title = title.text.strip()
      #print(title)
      link = article.find("link", class_=False)
      link = link.text.strip()
      if link.startswith("https://"): # check whether full link or partial link 
        link = link 
      else: 
        link = url_stub[0] + link
      #print(link)
      date = article.find("pubDate", class_=False)
      date = date.text.strip()
      #print(date)
      # todo: simplify data to uniform format 
      #description = article.find("description", class_=False)
      #description = description.text.strip()
      #print(description)      
      data_site = [time_now, union_data_rss["U-Union"][row], 
                   union_data_rss["U-Unit"][row], title, link, date, 
                   union_data_rss["U-URL"][row], union_data_rss["U-URL-Type"][row]]
      data_sites.append(data_site)
time_2 = time.time()
time_2 - time_1

# safe data
links_pickle = datetime.now().strftime("%Y_%m_%d") + "_links"
links_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{links_pickle}.pickle"
with open(links_pickle, "wb") as file:
  pickle.dump(data_sites, file)
  
  
  
  
  
  
      
      
      
      
      



### start of loop for vintage articles
# note: vintage sites slightly differ in their build...

  if union_data["U-URL-Type"][row] == "urlvint" and pd.isna(url):
    for x in range(0,5):
      # create URL, first site oftentimes not called "seite/1/" 
      if x == 0:
          url_new = union_data["U-URL"][row]
      if x != 0:
          url_new = union_data["U-URL"][row] + "?start=" + str(2022-x) + ".html"
      print(url_new)
      page = requests.get(url_new)
      soup = BeautifulSoup(page.content, "html.parser")
      results = soup.find(id="center-column-sub-page-right")
      if results is None: # stop iteration if ID not found (=no valid website)
          print("not valid")
          #break  
      print(union_data["U-Unit"][row])
      # finds all articles on the front page 
      #shorttext_elements = results.find_all("div", class_="teaserDisplay") # only shorttext and url
      headline_elements = results.find_all("h1", class_="teaserDisplay") # only headline
      date_elements = results.find_all("div", class_="teaserDisplayDate") # only date
      # safe interm. data 
      for news in range(len(date_elements)): 
        # headline element 
        headline = headline_elements[news]
        headline = re.findall('Display">(.*?)</h1', str(headline))
        print(headline)
        # date element 
        date = date_elements[news]
        date = re.findall('DisplayDate">(.*?)</div', str(date))
        print(date)
        url_news = date_elements[news]
        url_news = re.findall('href="(.*?)">', str(url_news))
        url_news = ["https://netkey40.igmetall.de" + x for x in url_news]    
        print(url_news)

      
