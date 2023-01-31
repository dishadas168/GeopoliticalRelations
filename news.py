"""
Extract news article details given news page url
"""

from helpers import (catch, news_article)
from utils import Article, BeautifulSoup, NewsPlease, get


class newspaper:

    def __init__(self, uri: str) -> bool:

        self.uri = uri

        """
        :return: Initializing the values with 'None', In case if the below values not able to extracted from the target uri
        """

        # NewsPlease Scraper
        newsplease = catch(
            'None', lambda: NewsPlease.from_url(self.uri, timeout=6))

        # Newspaper3K Scraper
        article = catch('None', lambda: Article(self.uri, timeout=6))
        catch('None', lambda: article.download())
        catch('None', lambda: article.parse())
        catch('None', lambda: article.nlp())

        soup = catch('None', lambda: BeautifulSoup(get(self.uri).text, 'lxml'))

        if all([newsplease, article, soup]) == None:
            raise ValueError(
                "Sorry, the page you are looking for doesn't exist'")

        """
        :returns: The News Article
        """
        self.article = catch('None', lambda: news_article(article.text) if article.text !=
                             None else news_article(newsplease.maintext) if newsplease.maintext != None else 'None')

        """
        :returns: keywords
        """
        self.keywords = catch('list', lambda: article.keywords)

        """
        :returns: summary
        """
        self.summary = catch('None', lambda: news_article(article.summary))

        """
        :returns: description
        """
        self.description = catch('None', lambda: news_article(article.meta_description) if article.meta_description != '' else news_article(
            article.meta_data['description']) if article.meta_data['description'] != {} else news_article(newsplease.description) if newsplease.description != None else None)

        """
        :returns: serializable_dict
        """
        self.get_dict = catch('dict', lambda: {
                                               'description': self.description,
                                               'article': self.article,
                                               'summary': self.summary,
                                               'keyword': self.keywords
        })