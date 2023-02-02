# analysing the data from the scraper 









# search for Streik and Warnstreik
for ... in ... 
if " Streik" in fulltext : 
    fulltext_streik = 1
else : 
    fulltext_streik = 0
if " Warnstreik" in fulltext : 
    fulltext_wstreik = 1
else : 
    fulltext_wstreik = 0
    
    
    






# Search for the keyword "strike" in the HTML
if "strike" in soup1.text:
    print("Keyword found on website 1!")
else:
    print("Keyword not found on website 1.")
