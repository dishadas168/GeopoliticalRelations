from fastapi import FastAPI
from routes.news import news_router
import uvicorn

app = FastAPI()
app.include_router(news_router)

if __name__ == "__main__":
    config = uvicorn.Config("index:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    server.run()