from pydantic import BaseModel
from typing import Dict

class Content(BaseModel):
    content : str
    parsed : str

class Meta(BaseModel):
    date: str

class Story(BaseModel):
    sents: Dict[str, Content]
    meta: Meta

class EventDict(BaseModel):
    events : Dict[str, Story]

