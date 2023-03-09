# industrial action tracking 
# Alexander Busch, contact@alexander-busch.eu

# todo
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
import pickle
import sys

# increase recursion limit to deal with saving complex data
sys.setrecursionlimit(9999999)

# read in url and unit 
union_data = pd.read_excel("union_data.xlsx", index_col=0) 
# select subsample
#union_data = union_data.iloc[0:10]
# website type distribution 
union_data["U-URL-Type"].value_counts()


## First: download webpages to lists
data_sites = []
for row in union_data.index: 
    # current time
    germany = timezone("Europe/Berlin")
    time_now = str(datetime.now(germany))
    # continue loop if url not encoded in scraper right now
    if union_data["U-URL-Type"][row] == "url1": 
        # loop for sub-sites of the news website (page 1, page 2, ...)
        for x in range(1,25):
            if x == 1: # create URL, first site oftentimes not called "seite/1/"
                url_new = union_data["U-URL"][row]
            else: 
                if union_data["U-Unit"][row]=="Dresden-Riesa": # exception for one unit 
                    url_new = union_data["U-URL"][row] + "seite-" + str(x)
                    print("Dresden")
                else:  
                    url_new = union_data["U-URL"][row] + "seite/" + str(x) + "/"
            print(url_new)
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
                         teaser_elements, union_data["U-URL-Type"][row]]
            data_sites.append(data_site)
    if union_data["U-URL-Type"][row] == "urlbw": 
        # loop for sub-sites of the news website (page 1, page 2, ...)
        for x in range(0,25):
            # create URL, first site oftentimes not called "seite/1/" 
            if x == 0:
                url_new = union_data["U-URL"][row]
            if x != 0:
                url_new = union_data["U-URL"][row] + "?start=" + str(x*20) + "/"
            print(url_new)
            page = requests.get(url_new)
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find(id="contentMain")
            ## go through articles, open them each and check whether they contain the word "strike"
            # finds all articles on the front page 
            teaser_elements = results.find_all("div", class_="entry")
            # stop when website not valid: does the html contain "teaser-text"?
            check = str(results)
            if "teaser" in check: 
                print("valid")
            else:
                print("not valid")
                break
            data_site = [url_new, time_now, union_data["U-Union"][row], 
                         union_data["U-Unit"][row], union_data["U-URL"][row], 
                         teaser_elements, union_data["U-URL-Type"][row]]
            data_sites.append(data_site)
    if union_data["U-URL-Type"][row] == "urlby": 
        url_new = union_data["U-URL"][row]
        page = requests.get(url_new)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="pageBody")
        # finds all articles on the front page 
        teaser_elements = results.find_all("a", class_="teaser")
        data_site = [url_new, time_now, union_data["U-Union"][row], 
                     union_data["U-Unit"][row], union_data["U-URL"][row], 
                     teaser_elements, union_data["U-URL-Type"][row]]
        data_sites.append(data_site)
        print("valid")


# safe data
with open("C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/data_sites.pickle", "wb") as file:
    pickle.dump(data_sites, file)

# open data 
with open("C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/data_sites.pickle", "rb") as file:
    data_sites = pickle.load(file)


## Second: organise data of webpages 
# -> something going on with bavaria, list index out of range? 
data = [["A-ID","A-Date","A-Version","A-Headline","A-Category","A-Shorttext",
         "A-Fulltext","A-URL","Date","U-Union","U-Unit","U-URL"]]

for teaser_website in range(len(data_sites)): 
    teaser_elements = data_sites[teaser_website][5]
    url = data_sites[teaser_website][4]
    #print(url)
    # stop when encounter link of last days top article
    #lastday = "https://www.igmetall-hanau-fulda.de/aktuelles/meldung/zentraler-warnstreik-kundgebung-und-demos-am-1711-in-hanau-gemeinsam-fuer-8-hoehere-entgelte-frieden-und-mehr-soziale-gerechtigkeit"
    # find out links and headlines of articles
    if data_sites[teaser_website][6] == "url1": 
        # shorten URL for below
        url_union_stub = re.findall(r"^https://www\.[a-z-_.]+\.de\/", url)
        #print(url_union_stub[0])
        #print("url1 found")
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
            fulltext_paragraphs = text_class.find_all("p")
            fulltext = "<<"
            for paragraph_element in fulltext_paragraphs:
                paragraph = paragraph_element.text.strip()
                #print(paragraph)
                fulltext = fulltext + ">>" + paragraph
            if fulltext == "<<": # if no paragraph, try to replace by shorttext
                fulltext = shorttext
            #print(fulltext)
            data_int = [1, date, 1, headline, category, shorttext, fulltext, url, 
                        data_sites[teaser_website][1], data_sites[teaser_website][2],
                        data_sites[teaser_website][3], data_sites[teaser_website][4]]
            data.append(data_int)
    if data_sites[teaser_website][6] == "urlbw": 
        for teaser_element in teaser_elements:
            link_element = teaser_element.find("a", class_=False)
            if link_element: 
                link = re.findall('href="(.*?)"', str(link_element))
                url = link[0]
                #print(url)
            date_element = teaser_element.find("tt", class_=False)
            if date_element: 
                date = date_element.text.strip()
                #print(date)
            # continue loop if current news was the final news of last day
            #if url == lastday: 
            #    continue
            # open subsite of specific news article 
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            news = soup.find(id="contentMain")
            news_elements = news.find("div", class_="article")
            headline_element = news_elements.find("h1", class_=False)
            headline = headline_element.text.strip()
            #print(headline)
            shorttext_element = news.find("div", class_="teaser")
            shorttext = shorttext_element.text.strip()
            shorttext = shorttext[11:] # remove date
            #print(shorttext)
            #fulltext_element = news_elements.find_all("div", class_="text")
            fulltext_element = news_elements.find_all("p", class_=False)
            fulltext = "<<"
            for paragraph in fulltext_element: 
                paragraph = paragraph.text.strip()
                if "Dateityp" in paragraph: 
                    break
                fulltext = fulltext + ">>" + paragraph
            if fulltext == "<<": # if no paragraph, try to replace by shorttext
                fulltext = shorttext
            fulltext = fulltext.strip()
            fulltext = fulltext[17:] # remove date
            fulltext = " ".join(fulltext.split()) # remove whitespace, \n, ...
            #print(fulltext)
            data_int = [1, date, 1, headline, "", shorttext, fulltext, url, 
                        data_sites[teaser_website][1], data_sites[teaser_website][2],
                        data_sites[teaser_website][3], data_sites[teaser_website][4]]
            data.append(data_int)
    if data_sites[teaser_website][6] == "urlby": 
        url_union_stub = re.findall(r"https?://[\w.-]+\.de/", url_new)
        for teaser_element in teaser_elements:
            link = re.findall('href="/(.*?)"', str(teaser_element))
            if not link: # continue if no link found, e.g. if refer to other website
                continue
            url = url_union_stub[0] + link[0]
            print(url)
            # continue loop if current news was the final news of last day
            #if url == lastday: 
            #    continue
            # open subsite of specific news article 
            headline = teaser_element.text.strip()
            print(headline)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            news = soup.find(id="pageBody")
            date = ""
            date = re.findall('class="d-md-none">(.*?)</b>', str(news))
            if date: 
                date = date[0].replace(" ","")
                print(date)
            category = ""
            categroy_element = ""
            category_element = news.find("h1", class_=False) 
            if category_element is None: # continue if not news-site, e.g. login required
                continue
            else: 
                category = re.findall('kicker">(.*?)</div>', str(category_element))
            if category: # if no category prevent error
                category = category[0]
                print(category)
            shorttext = ""
            shorttext_element = ""
            shorttext_element = news.find("h2", class_="p") 
            if shorttext_element: 
                shorttext = shorttext_element.text.strip()
                print(shorttext)
            fulltext = ""
            fulltext_element = ""
            fulltext_element = news.find("div", class_="col-sm-10 offset-sm-1 col-md-10 offset-md-1 col-lg-8 offset-lg-2")
            if fulltext_element: # exit if no text, e.g. if only pictures
                fulltext_element = fulltext_element.find_all("p", class_=False)
                fulltext = "<<"
                for paragraph in fulltext_element: 
                    paragraph = paragraph.text.strip()
                    fulltext = fulltext + ">>" + paragraph
                print(fulltext)
            data_int = [1, date, 1, headline, category, shorttext, fulltext, url, 
                        data_sites[teaser_website][1], data_sites[teaser_website][2],
                        data_sites[teaser_website][3], data_sites[teaser_website][4]]
            data.append(data_int)

# convert entries to data frame
length_list = len(data)-1
df = pd.DataFrame(data[1:length_list+1], columns=data[0])

df.to_excel('C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/data.xlsx')




### "VINTAGE" Design 


for x in range(0,5):
    # create URL, first site oftentimes not called "seite/1/" 
    if x == 0:
        url_new = union_data["U-URL"][row]
    if x != 0:
        url_new = union_data["U-URL"][row] + "?start=" + str(2022-x) + ".html"
    print(url_new)

data_sites = []

url_new = "https://netkey40.igmetall.de/homepages/bielefeld/"
# for x in ...
    
page = requests.get(url_new)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="center-column-sub-page-right")
if results is None: # stop iteration if ID not found (=no valid website)
    print("not valid")
    #break  
print("valid")
## go through articles, open them each and check whether they contain the word "strike"
# finds all articles on the front page 
shorttext_elements = results.find_all("div", class_="teaserDisplay") # only shorttext and url
headline_elements = results.find_all("h1", class_="teaserDisplay") # only headline
date_elements = results.find_all("div", class_="teaserDisplayDate") # only date
teaser_elements = [shorttext_elements, headline_elements, date_elements]
# safe interm. data 
data_site = [url_new, "time_now", "union_data[0][row]", 
             "union_data[2][row]", "union_data[1][row]", 
             teaser_elements, "union_data[3][row]"]
data_sites.append(data_site)

# open the specific sub sites of the webpage 

data = [["A-ID","A-Date","A-Version","A-Headline","A-Category","A-Shorttext",
         "A-Fulltext","A-URL","Date","U-Union","U-Unit","U-URL"]]

for teaser_website in range(len(data_sites)): 
    # extract shorttext element 
    shorttext = data_sites[teaser_website][5][0]
    shorttext = re.findall('Display">(.*?)<a href', str(shorttext))
    #print(shorttext)
    # headline element 
    headline = data_sites[teaser_website][5][1]
    headline = re.findall('Display">(.*?)</h1', str(headline))
    #print(headline)
    # date element 
    date = data_sites[teaser_website][5][2]
    date = re.findall('DisplayDate">(.*?)</div', str(date))
    #print(date)
    # url 
    #url_stub = data_sites[teaser_website][4]
    url = data_sites[teaser_website][5][0]
    url = re.findall('href="(.*?)">', str(url))
    url = ["https://netkey40.igmetall.de" + x for x in url]    
    #print(url)
    #if data_sites[teaser_website][6] == "urlvint": 
        for article in range(len(date)): # this is a counter! 
            # open subsite of specific news article 
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            news = soup.find(id="contentMain")
            news_elements = news.find("div", class_="article")
            headline_element = news_elements.find("h1", class_=False)
            headline = headline_element.text.strip()
            print(headline)
            shorttext_element = news.find("div", class_="teaser")
            shorttext = shorttext_element.text.strip()
            shorttext = shorttext[11:] # remove date
            print(shorttext)
            
            
            #fulltext_element = news_elements.find_all("div", class_="text")
            fulltext_element = news_elements.find_all("p", class_=False)
            fulltext = "<<"
            for paragraph in fulltext_element: 
                paragraph = paragraph.text.strip()
                if "Dateityp" in paragraph: 
                    break
                fulltext = fulltext + ">>" + paragraph
            if fulltext == "<<": # if no paragraph, try to replace by shorttext
                fulltext = shorttext
            fulltext = fulltext.strip()
            fulltext = fulltext[17:] # remove date
            fulltext = " ".join(fulltext.split()) # remove whitespace, \n, ...
            print(fulltext)
            
            data_int = [1, date, 1, headline, "", shorttext, fulltext, url, 
                        data_sites[teaser_website][1], data_sites[teaser_website][2],
                        data_sites[teaser_website][3], data_sites[teaser_website][4]]
            data.append(data_int)
            
            









### OLD BY CODE

url_new = "https://westmittelfranken.igmetall.de/aktuell"

url_union_stub = re.findall(r"https?://[\w.-]+\.de/", url_new)
print(url_union_stub)

page = requests.get(url_new)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="pageBody")
# finds all articles on the front page 
teaser_elements = results.find_all("a", class_="teaser")

data = [["A-ID","A-Date","A-Version","A-Headline","A-Category","A-Shorttext",
         "A-Fulltext","A-URL","Date","U-Union","U-Unit","U-URL"]]

for teaser_element in teaser_elements:
    link = re.findall('href="/(.*?)"', str(teaser_element))
    if not link: # continue if no link found, e.g. if refer to other website
        continue
    url = url_union_stub[0] + link[0]
    print(url)
    # continue loop if current news was the final news of last day
    #if url == lastday: 
    #    continue
    # open subsite of specific news article 
    headline = teaser_element.text.strip()
    print(headline)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    news = soup.find(id="pageBody")
    date = ""
    date = re.findall('class="d-md-none">(.*?)</b>', str(news))
    if date: 
        date = date[0].replace(" ","")
        print(date)
    category = ""
    category_element = news.find("h1", class_=False) 
    if category_element is None: # continue if not news-site, e.g. login required
        continue
    else: 
        category = re.findall('kicker">(.*?)</div>', str(category_element))
    if category: # if no category prevent error
        category = category[0]
        print(category)
    shorttext = ""
    shorttext_element = news.find("h2", class_="p") 
    if shorttext_element: 
        shorttext = shorttext_element.text.strip()
        print(shorttext)
    fulltext = ""
    fulltext_element = news.find("div", class_="col-sm-10 offset-sm-1 col-md-10 offset-md-1 col-lg-8 offset-lg-2")
    if fulltext_element: # exit if no text, e.g. if only pictures
        fulltext_element = fulltext_element.find_all("p", class_=False)
        fulltext = "<<"
        for paragraph in fulltext_element: 
            paragraph = paragraph.text.strip()
            fulltext = fulltext + ">>" + paragraph
        print(fulltext)
    data_int = [1, date, 1, headline, category, shorttext, fulltext, url, 
                "data_sites[teaser_website][1]", "data_sites[teaser_website][2]",
                "data_sites[teaser_website][3]", "data_sites[teaser_website][4]"]
    data.append(data_int)
    del fulltext_element
    del category_element

length_list = len(data)-1
df = pd.DataFrame(data[1:length_list+1], columns=data[0])






























# old BY code 
       
        
        for teaser_element in teaser_elements:
            headline = teaser_element.text.strip()
            #print(headline)
            link = re.findall('href="/aktuell(.*?)"', str(teaser_element))
            url = url_new + link[0]
            #print(url)
            # continue loop if current news was the final news of last day
            #if url == lastday: 
            #    continue
            # open subsite of specific news article 
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            news = soup.find(id="pageBody")
            date = ""
            date = re.findall('class="d-md-none">(.*?)</b>', str(news))
            if date: 
                date = date[0].replace(" ","")
            #print(str(date))
            category = ""
            category_element = news.find("h1", class_=False) 
            if category_element is None: # continue if not news-site, e.g. login required
                continue
            category = re.findall('"kicker">(.*?)</div>', str(news))
            category = category[0]
            #print(category)
            shorttext_element = news.find("h2", class_="p") 
            shorttext = shorttext_element.text.strip()
            #print(shorttext)
            fulltext_element = news.find("div", class_="col-sm-10 offset-sm-1 col-md-10 offset-md-1 col-lg-8 offset-lg-2")
            if fulltext_element is None: # exit if no text, e.g. if only pictures
                continue 
            fulltext_element = fulltext_element.find_all("p", class_=False)
            fulltext = "<<"
            for paragraph in fulltext_element: 
                paragraph = paragraph.text.strip()
                fulltext = fulltext + ">>" + paragraph
            #print(fulltext)
            data_int = [1, date, 1, headline, category, shorttext, fulltext, url, 
                        data_sites[teaser_website][1], data_sites[teaser_website][2],
                        data_sites[teaser_website][3], data_sites[teaser_website][4]]
            data.append(data_int)

