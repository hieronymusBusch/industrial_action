
# for the contemporaneous scraping, I use RSS feeds since the require less computing power / bandwith 
# RSS feeds do not reach back as far as the websites! 

#! pip install lxml
#! pip install html5lib

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone    
import pickle
import sys



r = requests.get('http://www.mannheim.igm.de/feed/news.xml')
soup = BeautifulSoup(r.content, features='xml')
print(soup)
articles = soup.findAll('item')



# what do: 
# 1. download contents of all sites in sample
# 2. check for duplicates (e.g. previously already downloaded)
# 3. if not duplicates, open sub-sites and scrape content 





