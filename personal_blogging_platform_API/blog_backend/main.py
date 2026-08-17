from fastapi import FastAPI, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime
from typing import Optional, List

from models import Article, ArticleCreate, ArticleUpdate
from database import get_db
from config import DATABASE_NAME

app = FastAPI(title="Personal Blogging API")

@app.on_event("startup")
async def startup():
    db = await get_db()
    app.state.articles = db.articles

@app.get("/articles", response_model=List[Article])
async def list_articles(
    db: AsyncIOMotorCollection = Depends(get_db),
    tag: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    query = {}
    if tag:
        query["tags"] = {"$in": [tag]}
    if start_date:
        query["published_at"] = {"$gte": start_date}
    if end_date:
        query["published_at"] = {"$lte": end_date}

    cursor = db.find(query).sort("published_at", -1)
    articles = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        articles.append(doc)
    return articles

@app.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str, db: AsyncIOMotorCollection = Depends(get_db)):
    article = await db.find_one({"_id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article["_id"] = str(article["_id"])
    return article

@app.post("/articles", response_model=Article, status_code=201)
async def create_article(article_data: ArticleCreate, db: AsyncIOMotorCollection = Depends(get_db)):
    article_dict = article_data.dict()
    article_dict["created_at"] = datetime.utcnow()
    article_dict["updated_at"] = datetime.utcnow()
    article_dict["published_at"] = article_dict.get("published_at") or datetime.utcnow()

    result = await db.insert_one(article_dict)
    article_dict["_id"] = str(result.inserted_id)
    return article_dict

@app.put("/articles/{article_id}", response_model=Article)
async def update_article(article_id: str, article_data: ArticleUpdate, db: AsyncIOMotorCollection = Depends(get_db)):
    article = await db.find_one({"_id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_dict = article_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()

    await db.update_one({"_id": article_id}, {"$set": update_dict})
    updated = await db.find_one({"_id": article_id})
    updated["_id"] = str(updated["_id"])
    return updated

@app.delete("/articles/{article_id}", status_code=204)
async def delete_article(article_id: str, db: AsyncIOMotorCollection = Depends(get_db)):
    result = await db.delete_one({"_id": article_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")