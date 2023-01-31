from datetime import datetime


def newsEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "authors": item["authors"],
        "title": item["title"],
        # "publish_date": item["publish_date"],
        "description": item["description"],
        "text": item["text"],
        "url": item["url"],
        "domain": item["domain"],
        "keywords": item["keywords"]
    }

def newsEntities(entities)-> list:
    return [newsEntity(item) for item in entities]