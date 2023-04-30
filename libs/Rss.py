import feedparser
import csv
import datetime
import os
from urllib.parse import urlparse
# date in yyyy/mm/dd format

class Rss:
    def __init__(self,filepath_rss):
        self.filepath_rss = filepath_rss
        self.rss_list = []
        self.articles_of_the_day_list = []
        self.set_rss_list()
        self.export_all_feeds()

    def set_rss_list(self):
        rss_feeds = open(self.filepath_rss, 'r')
        lines = rss_feeds.readlines()
        for line in lines:
            self.rss_list.append(line)
    
    def get_rss_list(self):
        return self.rss_list

    def convert_url_to_domain_name(self,url):
        domain = urlparse(url).netloc
        self.domain = domain

    def export_feed(self,url):
        self.convert_url_to_domain_name(url)
        print("Downloading article from", self.domain)
        if (self.domain == "www.ladepeche.fr"):
            return self.export_feed_ladepeche(url)
        elif (self.domain == "www.lemonde.fr"):
            return self.export_feed_lemonde(url)
        else:
            print("Impossible to export RSS feeds")

    def export_feed_ladepeche(self,url):
        path = "cache/" + urlparse(url).netloc + ".csv"
        news_feed = feedparser.parse(url)
        """print("Feed Link:", news_feed.feed.link)
        print("RSS Feed Keys :",news_feed.feed.keys())
        print("RSS Item Keys :",news_feed.entries[0].keys())

        for entry in news_feed.entries:
            print(f"{entry.published_parsed.tm_year} -- {entry.guidislink} ")
            
        for i in range(0, len(news_feed.entries)):
            if i == (len(news_feed.entries)-1):
                print("Alert: {} \nLink: {}".format(news_feed.entries[0]['title'], news_feed.entries[0]['id']))"""

        with open(path, 'a+', newline='', encoding="utf-8") as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONE, delimiter='|', quotechar='')
            for entry in news_feed.entries:
                spamwriter.writerow([str(entry.published_parsed.tm_year)+"/"+str(entry.published_parsed.tm_mon)+"/"+str(entry.published_parsed.tm_mday)+" "+str(entry.published_parsed.tm_hour)+":"+str(entry.published_parsed.tm_min)+":"+str(entry.published_parsed.tm_sec)] + [entry.link] + [False])

    def export_feed_lemonde(self,url):
        path = "cache/" + urlparse(url).netloc + ".csv"
        news_feed = feedparser.parse(url)
        """print("Feed Link:", news_feed.feed.link)
        print("RSS Feed Keys :",news_feed.feed.keys())
        print("RSS Item Keys :",news_feed.entries[0].keys())
        print(news_feed.entries[0].published_parsed.tm_year,news_feed.entries[0].published_parsed.tm_mon,news_feed.entries[0].published_parsed.tm_mday,news_feed.entries[0].published_parsed.tm_hour,news_feed.entries[0].published_parsed.tm_min,news_feed.entries[0].published_parsed.tm_sec,news_feed.entries[0].link)
"""
        """for entry in news_feed.entries:
            print(f"{entry.published_parsed.tm_year} -- {entry.guidislink} ")
            
        for i in range(0, len(news_feed.entries)):
            if i == (len(news_feed.entries)-1):
                print("Alert: {} \nLink: {}".format(news_feed.entries[0]['title'], news_feed.entries[0]['id']))"""
        with open(path, 'a+', newline='', encoding="utf-8") as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_NONE, delimiter='|', quotechar='')
            for entry in news_feed.entries:
                #print("writing row :",entry.published_parsed.tm_year,entry.published_parsed.tm_mon,entry.published_parsed.tm_mday,entry.published_parsed.tm_hour,entry.published_parsed.tm_min,entry.published_parsed.tm_sec,entry.link,"False")
                if("/live/" not in entry.link and "/appel-temoignages/" not in entry.link and "/video/" not in entry.link):
                    spamwriter.writerow([str(entry.published_parsed.tm_year)+"/"+str(entry.published_parsed.tm_mon)+"/"+str(entry.published_parsed.tm_mday)+" "+str(entry.published_parsed.tm_hour)+":"+str(entry.published_parsed.tm_min)+":"+str(entry.published_parsed.tm_sec)] + [entry.link] + [False])

    def export_all_feeds(self):
        dir_name = "cache/"
        test = os.listdir(dir_name)
        for item in test:
            if item.endswith(".csv"):
                os.remove(os.path.join(dir_name, item))
        for feed in self.rss_list:
            print("Processing feed :", feed)
            self.export_feed(url=feed)

    def articles_of_the_day(self):
        ct = datetime.datetime.now()
        ct_24h = ct - datetime.timedelta(days=1)
        articles_of_the_day = []
        for feed in self.rss_list:
            with open("cache/" + urlparse(feed).netloc +".csv", 'r') as file:
                csvreader = csv.reader(file, delimiter='|')
                for row in csvreader:
                    article_time = datetime.datetime.strptime(row[0], '%Y/%m/%d %H:%M:%S')
                    if(article_time < ct and article_time > ct_24h and row[2] == 'False'):
                        articles_of_the_day.append(row[1])
        self.articles_of_the_day_list = articles_of_the_day
        return articles_of_the_day

if __name__ == '__main__':
    rss = Rss(filepath_rss="config/rss_feeds")
    rss.export_all_feeds()
    print(rss.articles_of_the_day())