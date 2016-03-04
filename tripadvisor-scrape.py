#!/usr/bin/env python
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import sys
import csv
from datetime import datetime
import re
from collections import OrderedDict

MAX_ITEMS = 0
# DIVIDE IN EQUAL PARTS TO SCRAPE

def main():  
    print();
    print("This is " + sys.argv[0] + " by Tom van Nuenen.\nScrape tripadvisor, Deo Volente")
    print("--------------------------------------------------")
    global itemCount
    itemCount = 0        
    global fileName
    fileName = "tripadvisor_" + datetime.now().strftime('%Y%m%d_%H%M') + ".csv"
    global titleList
    titleList = []
    global writer
    fw = open(fileName, "w", newline='')
    writer = csv.writer(fw, delimiter=',', quoting=csv.QUOTE_MINIMAL)    
    writer.writerow(['number', 'link', 'date', 'title', 'text'])   
    print("The output CSV file is: %s " % (fileName))
    print("---------------------------------------------------------")
    # Start scraping on a first listing page. the function does its work and it also returns the url
    # of a 'volgende' index page OR it returns None to indicate that there are no further index pages    
    nextLink = "http://www.tripadvisor.com/ShowForum-g189398-i192-o24380-Greece.html" #BEGIN = "http://www.tripadvisor.com/ShowForum-g189398-i192-Greece.html"
    while nextLink != None and nextLink != "http://www.tripadvisor.com/ShowForum-g189398-i192-o171540-Greece.html":
        nextLink = analyzeIndexPage(nextLink)     
    # Done doing the scrape
    print("Process completed with %d stories" % (itemCount))

def analyzeIndexPage(url):
    print("analyzeIndexPage %s" % (url))
    host = urllib.parse.urlparse(url).netloc
    soup = BeautifulSoup(urllib.request.urlopen(url))    
    listLinks = []     
    for link in soup.findAll(href=re.compile("ShowTopic")):
        listLinks.append(link.get('href'))
    for l in listLinks:
        if "#" in l:
            lClean = l.split("#")[0]
            listLinks.append(lClean)
        if "#" in l:
            listLinks.remove(l)
    links = list(OrderedDict.fromkeys(listLinks))
    # Iterate again through all links in the list to analyze the relevant story pages
    for storyLink in links:
        analyzeStoryPage("http://" + host + storyLink)
    nextAnchor = soup.find("a", class_="guiArw sprite-pageNext")
    if nextAnchor:
        nextLink = nextAnchor.get('href')
        if (nextLink):
            nextLink = "http://" + host + nextLink
            return nextLink
    return None

def analyzeStoryPage(url):
    global itemCount, MAX_ITEMS, fileName
    if (MAX_ITEMS > 0) and (itemCount > MAX_ITEMS):
        print("Stopped the scrape after %d stories\n" % (MAX_ITEMS))
        sys.exit()
    # Show what page we're looking at 
    print("   %s - analyzeStoryPage %s" % (str(itemCount).zfill(5), url))
    try:    
        soup = BeautifulSoup(urllib.request.urlopen(url))
        divs = soup.findAll("div", class_="postcontent")
        for div in divs:
            itemCount += 1
            # Extract date
            date = div.find("div", class_="postDate").get_text().split(', ')[1]
            # Extract title
            title = div.find("div", class_="postTitle").get_text(" ", strip=True)
            # Extract text
            text = div.find("div", class_="postBody").get_text(" ", strip=True)
            # Check if duplicate of text or TripAdvisor post exists in textList 
            if "Message from TripAdvisor staff" not in text and title not in titleList:
                writer.writerow( (itemCount, url, date, title, text) )
                titleList.append(title)
        nextAnchor = soup.find("a", class_="guiArw sprite-pageNext")
        if nextAnchor:
            nextLink = nextAnchor.get('href')
            if (nextLink):
                nextLink = "http://www.tripadvisor.com/" + nextLink
                analyzeStoryPage(nextLink)
        return None
    except urllib.error.HTTPError as e:
        # Exception handling. Be verbose on HTTP errors such as 404 (not found).
        sys.stdout.write("    HTTPError: {0}\n".format(e))
        return
    except:
        # Exceptions thrown by operations on non-existing structures
        sys.stdout.write("    Structure exception: {0}\n".format(sys.exc_info()[0]))
        return

    

if __name__ == '__main__':
    main()#!/usr/bin/env python

