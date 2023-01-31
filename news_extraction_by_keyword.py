"""
Extract news articles given a Keyword
"""

import pandas as pd
from google import google_search
from news import newspaper
import requests

keyword= "Ukraine"
sites = ['https://www.wionews.com/',
         "https://www.theguardian.com/",
         "http://www.thedailybeast.com/",
         "https://news.yahoo.com/",
         "https://www.huffpost.com/",
         "https://www.cnn.com/",
         "https://www.nytimes.com/",
         "https://www.foxnews.com/",
         "https://www.nbcnews.com/",
         "https://www.bbc.com/news"
        ]

news_data_list = []

for site in sites:
    google_urls = google_search(keyword, site)
    for url in google_urls.urls:
        news = newspaper(url)
        news_data_list.append([news.authors, news.headline,\
                               news.date_publish, news.description,\
                               news.article, news.uri, site, news.keywords])
    print(google_urls.urls)
    print(f"Done for {site}")

