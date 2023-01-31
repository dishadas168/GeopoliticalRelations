"""
The Below functions contains error handling, unidecode, digits extraction, dataframe cleaning
"""

from utils import unidecode


errors = {'None': None, 'list': [], 'dict': {}}


def catch(default, func, handle=lambda e: e, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except:
        return errors[default]


def unicode(text: str) -> bool:
    return unidecode.unidecode(text).strip()


def news_article(text):
    return unicode(' '.join(text.replace('’', '').split()))



