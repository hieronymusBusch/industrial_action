# industrial action tracking 
# Alexander Busch, contact@alexander-busch.eu

# todo
# - move scraping to its own loop so that websites are saved at appr the same time, 
#   go over the content in a second step
# - include at least websites of type BW and BY for 100/140 coverage

#! pip install regex
#! pip install requests
#! pip install beautifulsoup4
#! pip install pandas
#! pip install openpyxl

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone    

# read in url and unit 
union_data = pd.read_excel("union_data.xlsx", index_col=0) 
# select subsample
#union_data = union_data.iloc[0:5]

# website type distribution 
#union_data["U-URL-Type"].value_counts()


## First: download webpages to lists
data_sites = []

for row in union_data.index: 
    # current time
    germany = timezone("Europe/Berlin")
    time_now = str(datetime.now(germany))
    # continue loop if url not encoded in scraper right now
    if union_data["U-URL-Type"][row] != "url1": 
        continue
    # loop for sub-sites of the news website (page 1, page 2, ...)
    for x in range(1,250):
        # create URL, first site oftentimes not called "seite/1/" 
        if x == 1:
            url_new = union_data["U-URL"][row]
        if x != 1:
            url_new = union_data["U-URL"][row] + "seite/" + str(x) + "/"
        #print(url_new)
        # page
        page = requests.get(url_new)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="folgeseite")
        ## go through articles, open them each and check whether they contain the word "strike"
        # finds all articles on the front page 
        teaser_elements = results.find_all("div", class_="news-list-content")
        # stop when website not valid: does the html contain "teaser-text"?
        check = str(results)
        if "teaser-text" in check: 
            print("valid")
        else:
            print("not valid")
            break
        data_site = [url_new, time_now, union_data["U-Union"][row], 
                     union_data["U-Unit"][row], union_data["U-URL"][row], 
                     teaser_elements]
        data_sites.append(data_site)


## Second: organise data of webpages 
data = [["A-ID","A-Date","A-Version","A-Headline","A-Category","A-Shorttext",
         "A-Fulltext","A-URL","Date","U-Union","U-Unit","U-URL"]]

for teaser_website in range(len(data_sites)): 
    teaser_elements = data_sites[teaser_website][5]
    url = data_sites[teaser_website][4]
    #print(url)
    # shorten URL for below
    url_union_stub = re.findall(r"^https://www\.[a-z-_]+\.de\/", url)
    #print(url_union_stub[0])
    # stop when encounter link of last days top article
    #lastday = "https://www.igmetall-hanau-fulda.de/aktuelles/meldung/zentraler-warnstreik-kundgebung-und-demos-am-1711-in-hanau-gemeinsam-fuer-8-hoehere-entgelte-frieden-und-mehr-soziale-gerechtigkeit"
    # find out links and headlines of articles
    for teaser_element in teaser_elements:
        # first, look at the link: if there is no link, the website is not valid! 
        link_element = teaser_element.find("a", class_=False)
        if link_element: 
            link = re.findall('href="(.*?)"', str(link_element))
            url = url_union_stub[0] + link[0]
            #print(url)
        category_element = teaser_element.find("h4", class_="newsheadline")
        if category_element: # the if conditions make sure the script runs if an element is empty 
            category = category_element.text.strip()
            #print(category)
        date_element = teaser_element.find("li", class_=False)
        if date_element: 
            date = date_element.text.strip()
            #print(date)
        shorttext_element = teaser_element.find("div", class_="teaser-text")
        if shorttext_element: 
            shorttext = shorttext_element.text.strip()
            #print(shorttext)
        # continue loop if current news was the final news of last day
        #if url == lastday: 
        #    continue
        # open subsite of specific news article 
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        news = soup.find(id="folgeseite")
        news_elements = news.find("div", class_="news-single-item")
        headline_element = news_elements.find_all("h2", class_=False)
        headline = re.findall('<h2>(.*?)</h2>', str(headline_element))
        headline = headline[0]
        #print(headline)
        text_class = news.find("div", class_="news-text")
        fulltext_paragraphs = text_class.find_all("p", class_=False)
        fulltext = shorttext
        for paragraph in fulltext_paragraphs:
            paragraph2 = paragraph.text.strip()
            #print(paragraph)
            fulltext = fulltext + ">>>>" + paragraph2
        #print(fulltext)
        data_int = [1, date, 1, headline, category, shorttext, fulltext, url, 
                    data_sites[teaser_website][1], data_sites[teaser_website][2],
                    data_sites[teaser_website][3], data_sites[teaser_website][4]]
        data.append(data_int)
        
# convert entries to data frame
length_list = len(data)-1
df = pd.DataFrame(data[1:length_list+1], columns=data[0])













