"""
Extract news articles given a Google news category
"""

from news import newspaper
from utils import bs4, BeautifulSoup, requests, datetime, timedelta


QUERY_STRINGS = {"World" : "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "US" : "topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE?hl=en-US&gl=US&ceid=US%3Aen",
                 "Business" : "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "Technology": "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "Entertainment" : "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "Sports" : "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "Science" : "topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
                 "Health" : "topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-US&gl=US&ceid=US%3Aen"
                 }

def get_urls(q_string):
    """
    Extract news urls for a Google News Category
    """
    BASE_URL = "https://news.google.com"
    news_list = []
    for category, q_string in QUERY_STRINGS.items():
        news = requests.get(f"{BASE_URL}/{q_string}")
        soup = BeautifulSoup(news.text, "html.parser")

        for article in soup.select("article"):

            date = article.select("div div time")[0].get("datetime")
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

            if date > datetime.now() + timedelta(hours=-24):
                title = article.select("h3 a")

                if not title:
                    title = article.select("h4 a")[0].text
                    url = article.select("h4 a")[0].get("href")
                elif type(title) == bs4.element.ResultSet:
                    url = title[0].get("href")
                    title = title[0].text

                news_list.append({
                    "title": title,
                    "url": f"{BASE_URL}/{url}",
                    "category" : category,
                    "publish_datetime" : date
                })

    return news_list

def get_article_details(news_list):
    """
    Extract news article information from news urls
    """
    for id, site in enumerate(news_list):
        news = newspaper(site["url"])

        if len(news.article) > 0:
            #TODO: Check if article exists in dynamodb, then proceed

            news_list[id]["description"] = news.description
            news_list[id]["text"] = news.article
            news_list[id]["keywords"] = news.keywords

        print(f"Done {id}/{len(news_list)}")

# Send to MongoDB db
# conn_url = "http://127.0.0.1:8000/insert_article"
# response = requests.post(conn_url, json=article)


news_list = get_urls(QUERY_STRINGS["World"])
print(len(news_list))
news_list_details = get_article_details(news_list)