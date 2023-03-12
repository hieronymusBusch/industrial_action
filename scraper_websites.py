################################################################################
###
### date creation: 2023-03-06
### author: Alexander Busch (busch@iza.org)
### project: strike tracker (with coauthors)
###
###
### this file: 
###   - uses the provided links from other files to scrape the websites behind it
###   - output is 
###     - current date data set
###     - linked data set of all previous dates 
###
################################################################################

# second step: using links provided by scraper_links to scrape press releases from websites 

# adds the following variables: 
#   - site_headline, site_shorttext, site_fulltext, site_date, 

# to do: 
# - safe one copy of current daily data & a merged version
# - implement "vintage" URLS and IGM-NRW into feed
# - automate on server 
# - run and safe historic version 
# - integrate url2 option / igm nrw in rss scraping 
# - integrate dates of urlby articles (no date on site)

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

# setup 
#pd.set_option('display.max_rows', 300)
sys.setrecursionlimit(9999999)

# timer for script
time_start = time.time()


## open link-data 

# current day data 
links_pickle = datetime.now().strftime("%Y_%m_%d") + "_links"
links_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{links_pickle}.pickle"
with open(links_pickle, "rb") as file:  
  data_sites = pickle.load(file)
#memo_pickle = datetime.now().strftime("%Y_%m_%d") + "_memo"
#memo_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{memo_pickle}.pickle"
#with open(memo_pickle, "rb") as file:  
#  memo = pickle.load(file)
# open all data
all_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/all_pickle.pickle"
with open(all_pickle, "rb") as file:  
  df_all = pickle.load(file)


## prepare links to be analysed 

# convert entries to data frame
df_names = [["union","union_section","union_url","union_url_type","link_headline",
             "link_url","link_date","link_url_type","scrape_date","scrape_page",
             "link_date_std","local"]]
length_list = len(links)-1
df = pd.DataFrame(links[0:length_list+1], columns=df_names)

# create empty df
df_all = pd.DataFrame(columns=["news_id","scrape_version","scrape_date","news_date",
                               "news_headline","news_shorttext","news_fulltext",
                               "news_url","union","union_section","union_url"])

# case 1: no previous data, set id to 0 and set previous data counter to 3
c_news_id = 0

# case 2: load all data, set id to max id of historic dat a
#all_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/df_all.pickle"
#with open(all_pickle, "rb") as file: # data frame of all combined days
#  df_all = pickle.load(file)
#c_news_id = max(df_all["news_id"]) # counter news_id starting from max. prev. ID

# case 3: test run, simulate some historic data based on data in memory 
#df1 = df.sample(n=300, random_state=1)
#df2 = df1.sample(n=100, random_state=1)
#df_all = pd.concat([df1, df2], ignore_index=True)
#df_all["news_id"] = range(1, len(df_all) + 1) # simulate identifier
#c_news_id = max(df_all["news_id"]) # counter news_id starting from max. prev. ID

# collapse data in memory to one entry per unit for testing
#df_test = df.drop_duplicates(subset=["union_section"])
#df_test.drop(df_test.loc[df_test["union_section"] == "IGM-Ost"].index, inplace=True)
#press_list = df_test.values.tolist()

# convert to data frame 
press_list = df_test.values.tolist()


## analysing content of press releases 
time_3 = time.time()
data = [["news_id","scrape_version","scrape_date","news_date","news_headline",
         "news_shorttext","news_fulltext","news_url","union","union_section","union_url"]]
for press_link in range(len(press_list)): 
  # create empty values to facilitate evaluation of objects and drop previous vaues
  empty_values = ["link", "rep", "page", "soup", "news", "news_elements", "headline", "shorttext"]
  for var_name in empty_values:
    exec(f"{var_name} = ''")
  link = press_list[press_link][4] # select link from RSS feed
  if (df_all["news_url"] == link).sum() == 3:
    print(f"Link is already 3x in the data frame.")
    continue
  rep = (df_all["news_url"] == link).sum()+1 # is this the 1th, 2nd, 3rd entry of the same article? 
  #print(rep)
  # now sub-site specific scraping 
  if press_list[press_link][7] in ["url1", "url11", "urlby", "urlby1", "urlbw"]: 
  # do this in the specific part to only give valid links an id 
    if rep==1: 
      c_news_id = c_news_id + 1 # create ID if press release just enters the data base 
      news_id = c_news_id
    else: 
      news_id = df_all[df_all["news_url"]==link].iloc[0].at["news_id"] # pull old ID from data
    #print(news_id)
    print(link)
    # open subsite of specific news article, robust to temp unavailable website
    try:
      page = requests.get(link)
      soup = BeautifulSoup(page.content, "html.parser")
    except requests.exceptions.RequestException as e:
      print("Error: Unable to connect to website")
      data_int = [news_id, rep, press_list[press_link][0], press_list[press_link][5], "headline", "shorttext", "fulltext", link, press_list[press_link][1], press_list[press_link][2], press_list[press_link][6]]
      data.append(data_int)
      continue
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    # matching possible ID's: url1, url11, url11 hannover, url11 nienburg, url11 B Mitte, sued-nieds., urlbw
    possible_ids = ["folgeseite", "folge", "pageBody", "content", "c833", "c8", "c53", "contentMain"] 
    for id in possible_ids:
      news = soup.find(id=id)
      if news:
        break    
    news_elements = news.find("div", class_="news-single-item")
    if not news_elements: 
      news_elements = news.find("div", class_="article") # urlbw
    # headline
    if not news_elements or press_list[press_link][7]=="urlbw": # urlby case, no "div" class with all info, also works for urlbw
      headline = str(news.find("h1", class_=False)) # double quotes necessary because of "" in string
      headline = headline.replace('<h1>', '').replace('<div class=\"kicker\">', '').replace('</div>', '').replace('</h1>', '').replace('\n', '')
    if news_elements and press_list[press_link][7]!="urlbw": # other url1 and url11 cases: find h2, if not h1
      headline = news_elements.find_all("h2", class_=False) # url1
      if headline: 
        headline = re.findall('<h2>(.*?)</h2>', str(headline)) 
        headline = headline[0]
      if not headline or headline=="Zum Thema": # website of dresden has h2 element "zum Thema"
        headline = news_elements.find_all("h1", class_=False) # url11
        if headline: 
          headline = re.findall('<h1>(.*?)</h1>', str(headline)) 
          headline = headline[0]
    #print(headline)
    # shorttext
    shorttext = re.findall('\s*<em>(.*?)</em>\s*', str(news), re.DOTALL)
    if not shorttext: # urlby case 
      shorttext = news.find("div", class_="col-sm-12")
      shorttext = re.findall('\s*\"p\">(.*?)</h2>\s*', str(news), re.DOTALL)
    if shorttext: # if shorttext through findall
      shorttext = shorttext[0]      
    if not shorttext and press_list[press_link][7]=="urlbw": # urlbw case, can cause problems in other urls
      shorttext = news.find("div", class_="teaser")
      shorttext = shorttext.text.strip()
      shorttext = shorttext[11:] # remove date
    if not shorttext: # if neither of the above, no shorttext assumed
      shorttext = ""
      print("no shorttext")
    #print(shorttext)
    # full text
    fulltext_paragraphs = news.find("div", class_="news-text")
    if not fulltext_paragraphs: # güthersloh
      fulltext_paragraphs = news.find("div", class_="news-text-wrap") 
    if not fulltext_paragraphs: # urlby
      fulltext_paragraphs = news.find("div", class_="col-sm-10 offset-sm-1 col-md-10 offset-md-1 col-lg-8 offset-lg-2")
    if not fulltext_paragraphs and press_list[press_link][7]=="urlbw": # urlbw
      fulltext_paragraphs = news_elements.find("div", class_="text")
    fulltext = shorttext # every fulltext starts with the shorttext 
    if fulltext_paragraphs: # there may be no text, only pictures
      #fulltext = fulltext_paragraphs.replace('<ul>', '').replace('<\ul>', ' ').replace('<ul>', '').replace('</p>', ' ').replace('</p>', ' ').replace('\n', '')
      fulltext_paragraphs = fulltext_paragraphs.find_all("p")
      for paragraph_element in fulltext_paragraphs:
        paragraph = paragraph_element.text.strip()
        fulltext = fulltext + ">>" + paragraph
    if fulltext==shorttext: 
      print("no fulltext")
    #print(fulltext)
    if fulltext!=shorttext: 
      print("fulltext")
    data_int = [news_id, rep, press_list[press_link][0], press_list[press_link][5], 
                headline, shorttext, fulltext, link, press_list[press_link][1], 
                press_list[press_link][2], press_list[press_link][6]]
    data.append(data_int)
  if press_link+1==len(press_list): 
    print("successful run")
    
time_4 = time.time()
(time_4 - time_3)/60

# safe data
content_pickle = datetime.now().strftime("%Y_%m_%d") + "_content"
content_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{content_pickle}.pickle"
with open(content_pickle, "wb") as file:
  pickle.dump(data, file)

# open data 
with open(content_pickle, "rb") as file:
  data = pickle.load(file)

# convert entries to data frame
length_list = len(data)-1
df = pd.DataFrame(data[1:length_list+1], columns=data[0])

# convert date formats 
def convert_to_correct_format(date_str):
    try:
        date = parse(date_str)
        return date.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            date = pd.to_datetime(date_str, format='%a, %d %b %Y %H:%M:%S %z')
            return date.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return date_str
df['news_date'] = df['news_date'].apply(convert_to_correct_format)
df['news_date'] = pd.to_datetime(df['news_date'])
df['news_date_year'] = df['news_date'].dt.year
df['news_date_year_month'] = df['news_date'].dt.strftime('%Y-%m')

# add to full data list 
df_all = pd.concat([df_all, df], ignore_index=True)

# safe data
data_pickle = datetime.now().strftime("%Y_%m_%d") + "_data"
data_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{data_pickle}.pickle"
with open(data_pickle, "wb") as file:
  pickle.dump(df, file)
df.to_csv('C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/{data_pickle}.csv', index=False)

with open(all_pickle, "wb") as file:
  pickle.dump(df_all, file)
df.to_csv('C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/df_all.csv', index=False)












## some first metrics 

# calculate run times
time_2 - time_1 # first loop
time_4 - time_3 # second loop 

# distribution of press releases in 2/3 convenience sample RSS
counts_year = df["news_date_year"].value_counts()
counts_year
counts_year/length_list

grouped = ((df['news_fulltext'].str.contains('streik')).sum() + (df['news_headline'].str.contains('streik')).sum())
total_counts = len(df)
counts_share_strike = grouped.sum() / total_counts
counts_share_strike

counts = df["news_date_year_month"].value_counts()
counts 
counts/length_list
# plot the counts
year_months = [str(idx) for idx in counts.index]
year_months.sort()
plt.figure(figsize=(10,5))
counts.loc[year_months].plot(kind='bar')
plt.xlabel('Year-Month')
plt.ylabel('Count')
plt.title('Observations per Year-Month')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
xticklabels = [year_months[i] if year_months[i][-2:] in ('01', '07') else '' for i in range(len(year_months))]
plt.gca().set_xticklabels(xticklabels)
# save plot as pdf and png
pdf = matplotlib.backends.backend_pdf.PdfPages("C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/count.pdf")
pdf.savefig()
pdf.close()
plt.savefig('C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/count.png')
plt.show()

# share of press releases containing the string "strike"
grouped = df.groupby('news_date_year_month').apply(lambda x: ((x['news_fulltext'].str.contains('streik')).sum() + (x['news_headline'].str.contains('streik')).sum()))
total_counts = df["news_date_year_month"].value_counts()
counts_share_strike = grouped / total_counts
# plot the counts
year_months = [str(idx) for idx in counts_share_strike.index]
year_months.sort()
plt.figure(figsize=(10,5))
counts_share_strike.loc[year_months].plot(kind='bar')
plt.xlabel('Year-Month')
plt.ylabel('Share of Texts / Headlines including Streik')
plt.title('Share of Streik-mentions per Year-Month')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
xticklabels = [year_months[i] if year_months[i][-2:] in ('01', '07') else '' for i in range(len(year_months))]
plt.gca().set_xticklabels(xticklabels)
# save plot as pdf and png
pdf = matplotlib.backends.backend_pdf.PdfPages("C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/count_strike.pdf")
pdf.savefig()
pdf.close()
plt.savefig('C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/count_strike.png')
plt.show()


