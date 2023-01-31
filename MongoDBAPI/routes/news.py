from fastapi import APIRouter
from schemas.news import newsEntity, newsEntities
from models.news import GatheredNews
from config.db import conn
from typing import List
from bson import ObjectId

news_router = APIRouter()

@news_router.get('/')
async def find_all_articles():
    return newsEntities(conn.news_data.gathered_news.find({}))

@news_router.post('/insert_article')
async def create_articles(article: GatheredNews):

    #Redirect new urls to url_staging table for processing
    if conn.news_data.gathered_news.count_documents({"url": article.url}) == 0:
        print(article.url)
        stage_doc = {
            "url" : article.url
        }
        conn.news_data.url_staging.insert_one(dict(stage_doc))
        conn.news_data.gathered_news.insert_one(dict(article))
    return newsEntities(conn.news_data.gathered_news.find({}))

# @news_router.post('/')
# async def create_article(article: GatheredNews):
#     conn.news_data.gathered_news.insert_one(dict(article))
#     return newsEntities(conn.news_data.gathered_news.find({}))

# @news_router.delete('/{id}')
# async def delete_article(id, article: GatheredNews):
#     return newsEntity(conn.news_data.gathered_news.find_one_and_delete({"_id": ObjectId(id)}) )