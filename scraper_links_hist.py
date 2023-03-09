################################################################################
###
### date creation: 2023-03-06
### author: Alexander Busch (busch@iza.org)
### project: strike tracker (with coauthors)
###
###
### this file: 
###   - scrapes website-links of previous press releases of trade unions
###   - is the starting point of the actual scraper which ignores historic links 
###
################################################################################


## safe links: website
# in general, this code follows the structure that most websites...
#  ... contain subgroups for each article listed
#  ... each subgroup contains a date, a link, and a headline
#  ... but they might have different naming conventions depending on the site 

# hist_links_errors: 
#  the error_list lists whether there was an error that would otherwise have 
#  stopped the code from execution (e.g. no connection to website)

# hist_links: 
#   contains all available info about link: which union, which locality, union_url, 
#       the type of url (e.g. "urlbw") to decide which code to use for webscraping, 
#       the headline, the url of the press release itself, the type of url of the link
#       (most likely the same as the type of url of the "mothersite"), and the scraping time / date

# to do: 
# - integrate "vintage"/individual URLS and IGM-NRW: currently 22 websites not scraped! 
# - integrate DATES of url2 and igm main website
# - run and safe historic version 

# setup 
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import time
from dateutil.parser import parse
#pd.set_option('display.max_rows', 300)
sys.setrecursionlimit(9999999)

# timer for script
time_start = time.time()



### looping over websites with press releases


## prepare data frame with press release website links 

# union information (links etc.)
union_data_hist = pd.read_excel("union_data.xlsx", sheet_name="hist", index_col=0)
# create url_stubs 
def extract_url_stub(url):
    url_stub = re.findall(r"^(https?:\/\/[a-z-_.]+\.de)\/", url)
    return url_stub[0] if url_stub else url
union_data_hist['union_url_stub'] = union_data_hist['U-URL'].apply(extract_url_stub)
# define empty lists for loop 
hist_links = [["union","union_section","union_url","union_url_type","link_headline",
               "link_url","link_date","link_url_type","scrape_date"]]
hist_links_errors = []


## looping over websites 
for row in union_data_hist.index: 
  # continue loop if url not encoded in scraper right now
  if union_data_hist["U-URL-Type"][row] in ["url1", "urlby", "urlby1", "urlbw", "url2", "url11"]: 
    # reset values
    empty_values = ["link_title","link_url","link_date","link_url_type","scrape_date",
                    "url_new","page","soup","results","error","press_releases","date_element"]
    for var_name in empty_values:
      exec(f"{var_name} = ''")
    # current time
    germany = timezone("Europe/Berlin")
    scrape_date = str(datetime.now(germany))
    # loop for sub-sites of the news website (page 1, page 2, ...)
    for x in range(1,2): # this is range[beginning,end) !!!
      if x==1: # create URL, first site oftentimes not called "seite/1/"
        url_new = union_data_hist["U-URL"][row]
      if x>1 and union_data_hist["U-URL-Type"][row] in ["url1", "url11", "url2"]: # url1 structure 
        if union_data_hist["U-Unit"][row]=="Gelsenkirchen": # exception for one unit 
          url_new = union_data_hist["U-URL"][row] + "page/" + str(x) + "/"
        elif union_data_hist["U-Unit"][row]=="Dresden-Riesa": # exception for one unit 
          url_new = union_data_hist["U-URL"][row] + "seite-" + str(x)
        #elif union_data_hist["U-Unit"][row]=="Ludwigsburg-Waiblingen": # exception for one unit 
          #url_new = union_data_hist["U-URL"][row] + "node?page=" + str(x-1)
          #print("waiblingen test")
        elif union_data_hist["U-URL-Type"][row]=="url2" and next_link: # url2 structure, only if next_link exists (ie not past final page) 
          url_new = union_data_hist["union_url_stub"][row] + "/" + next_link[0]
        else:  
          url_new = union_data_hist["U-URL"][row] + "seite/" + str(x) + "/"
      if x>1 and union_data_hist["U-URL-Type"][row]=="urlbw": # urlbw structure 
        url_new = union_data_hist["U-URL"][row] + "?start=" + str(x*20) + "/"
      if x>1 and (union_data_hist["U-URL-Type"][row]=="urlby" or union_data_hist["U-Unit"][row]=="IGM-Aktuelles"): # no second page for urlby / IGM main website
        break 
      print(url_new)
      # load page, continue if server not responsive 
      try: 
        page = requests.get(url_new, timeout=15) # timeout set to max 5 seconds of waiting for server 
        soup = BeautifulSoup(page.content, "html.parser")
      except (requests.exceptions.RequestException, TimeoutError) as e:
          error = ["page_error", url_new] # set error_parameter to "page_error"
          hist_links_errors.append(error) # list of errors
          continue
      # load page ID 
      possible_ids = ["folgeseite", "folge-content", "folge", "pageBody", "content", 
                      "c833", "c8", "c11", "c53", "c840", "contentMain", "main-content", 
                      "page-content", "c133", "shortcutContent"] 
      for id in possible_ids:
        results = soup.find(id=id)
        if results:
          break 
      if not results: 
        results = soup.find("div", class_="news-list-view")
      # for url2-type: find link for next site (for url2, the urls are not trivial!)
      if union_data_hist["U-URL-Type"][row]=="url2": 
        next_link = results.find("li", class_="last next")
        next_link = re.findall(r'<a href="/([^"]*)"', str(next_link))
      # finds all articles on the front page 
      press_releases = results.find_all("a", class_="spanAllLink") # url11 / 1
      if not press_releases: 
        press_releases = results.select("div.news-list-content > div.news-list-content") # url11 / 1: nienburg (has nested objects with the same name)
      if not press_releases: 
        press_releases = results.find_all("div", class_="news-list-content") # url11 / 1
      if not press_releases: 
        press_releases = results.find_all("div", class_="news-list-content card-body") # url11 wolfsburg
      if not press_releases: 
        press_releases = results.find_all("a", class_="teaser") # url11 / 1, also urlby
      if not press_releases: 
        press_releases = results.find_all("div", class_="entry") # urlbw
      if not press_releases: 
        press_releases = results.find_all("div", class_="article articletype-0") # url2 & IGM NRW
      if press_releases: 
        for press_release in press_releases: 
          # press release link 
          link = re.findall('\s*href="(.*?)"\s*', str(press_release), re.DOTALL)
          if link: 
            #print(link)
            if link[0].startswith("https://"): # check whether full link or partial link 
              link_url = link[0]
            else: 
              link_url = union_data_hist["union_url_stub"][row] + link[0] 
            print(link_url)
          # headline
          link_title = press_release.find("h2") # e.g. url2
          if not link_title: 
            link_title = press_release.find("h1")
          if not link_title: 
            link_title = press_release.find("h4", class_="newsheadline") 
          if link_title: 
            link_title = link_title.text.strip()
            print(link_title)
          # date 
          date_element = press_release.find("li") # most url1 websites
          if not date_element: 
            link_date = re.findall(r'class="teaser-date">([^<]*)</p>', str(press_release)) # case for IGM main
            if not link_date: 
              link_date = re.findall(r'class="updated">([^<]*)"</span>', str(press_release)) # url2, gelsenkirchen
            if not link_date:
              link_date = re.findall(r'class="news-list-date">([^<]*)</span>', str(press_release)) # url2
            if link_date: 
              link_date = link_date[0]
          if not (date_element or link_date): 
            date_element = press_release.find("tt", class_=False) # urlbw
          if not (date_element or link_date) and not (union_data_hist["U-URL-Type"][row] in ["urlby", "urlby1"]): # no urlby
            date_element = press_release.find("span") # e.g. Leipzig, Hannover, Dresden-Riesa, NRW IGM
          if date_element: 
            link_date = date_element.text.strip()
          if not link_date: # urlby has no date 
            link_date = ""
          #print(link_date)
          # check type of link (e.g. whether it's website type is "urlbw")  
          try:
            link_stub = re.findall(r"^(https?:\/\/[a-z-_.]+\.de)\/", link_url)[0] # extract stub
            link_row = union_data_hist[union_data_hist["union_url_stub"] == link_stub].iloc[0] # identify matching row
            link_url_type = link_row['U-URL-Type'] # extract url type of said row
          except IndexError: # if external (=not in data base) link
              link_url_type = "url_external"
          #print(link_url_type)
          # save data 
          hist_link = [union_data_hist["U-Union"][row], union_data_hist["U-Unit"][row], 
                            union_data_hist["U-URL"][row], union_data_hist["U-URL-Type"][row], 
                            link_title, link_url, link_date, link_url_type, scrape_date]
          hist_links.append(hist_link) # scraped results
          print("added to hist_links")
  if row+1==len(union_data_hist): 
    print("successful run")
        


### first data clean operations
length_list = len(hist_links)-1
df = pd.DataFrame(hist_links[1:length_list+1], columns=hist_links[0])

# convert to uniform data format DD.MM.YYYY
def extract_date(text):
    # Check for format "dd.mm.yyyy"
    match = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', text)
    if match:
        day = match.group(1)
        if len(day) == 1:
            day = '0' + day
        month = match.group(2)
        if len(month) == 1:
            month = '0' + month
        year = match.group(3)
        return datetime.date(int(year), int(month), int(day)).strftime('%d.%m.%Y')
    # Check for format "d. Month yyyy"
    match = re.search(r'(\d{1,2})\.\s*([^\d\s]+)\s*(\d{4})', text)
    if match:
        day = match.group(1)
        if len(day) == 1:
            day = '0' + day
        month = match.group(2)
        year = match.group(3)
        # Convert month name to month number
        try:
            month_num = datetime.datetime.strptime(month, '%B').month
            return datetime.date(int(year), month_num, int(day)).strftime('%d.%m.%Y')
        except ValueError:
            pass
    return ''
df['link_date'] = df['link_date'].apply(extract_date)


## Drop duplicate links, keep instance from own website if possible 
# mark duplicates
duplicate_counts = df.groupby('link_url').size()
df['duplicate_count'] = df['link_url'].map(duplicate_counts)
# mark local links (press release urls from same main url)
df["link_local"] = df["union_url"].str.extract(r"(https?://([a-z0-9.-]+\.[a-z]{2,}))", flags=re.IGNORECASE)[0].eq(
    df["link_url"].str.extract(r"(https?://([a-z0-9.-]+\.[a-z]{2,}))", flags=re.IGNORECASE)[0])
# Drop duplicates and keep local instance if possible
df.sort_values(['link_url', 'link_local'], ascending=[True, False], inplace=True)
df.drop_duplicates(subset=['link_url'], keep='first', inplace=True)
# double check duplicate count
duplicate_counts = df.groupby('link_url').size()
df['duplicate_count'] = df['link_url'].map(duplicate_counts)
df.drop('duplicate_count', axis=1, inplace=True)
# convert back to list 
hist_links = df.values.tolist()


## safe data
hist_links_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/hist_links_pickle.pickle"
with open(hist_links_pickle, "wb") as file:
  pickle.dump(hist_links, file)
hist_links_errors_pickle = f"C:/Users/AlexBusch/Dropbox/Industrial_Action/data/web_scraper/hist_links_errors.pickle"
with open(hist_links_errors_pickle, "wb") as file:
  pickle.dump(hist_links_errors, file)

time_end = time.time()
elapsed_time = (time_end - time_start)/60 # elapsed time in minutes 
print(elapsed_time)




