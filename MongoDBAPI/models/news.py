from datetime import datetime
from pydantic import BaseModel
from typing import List

class GatheredNews(BaseModel):
    authors: list[str]
    title: str
    # publish_date: datetime
    description: str
    text: str
    url: str
    domain: str
    keywords: list[str]

class URLStaging(BaseModel):
    url: str
