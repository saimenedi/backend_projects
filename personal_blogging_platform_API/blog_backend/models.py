from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: List[str] = []
    published_at: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None

class Article(ArticleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True