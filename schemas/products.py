from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Base schema for shared fields
class ProductBase(BaseModel):
    title: str
    one_liner: Optional[str] = None
    description: Optional[str] = None
    price: float
    discounted_price: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    dimensions: Optional[str] = None
    slug: Optional[str] = None  # optional, generated if missing

# Input schema for creation (no created_at/updated_at)
class ProductCreate(ProductBase):
    pass

# Response schema
class ProductResponse(BaseModel):
    id: int
    title: str
    one_liner: Optional[str]
    description: Optional[str]
    image_links: List[str] = []
    price: float
    discounted_price: Optional[float]
    category: Optional[str]
    subcategory: Optional[str]
    dimensions: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
        


class ProductAnalyticsSchema(BaseModel):
    view_count: int
    purchase_count: int
    rating: float
    review_count: int
    stock_count: int
    wishlist_count: int

    class Config:
        from_attributes = True


class PaginatedProducts(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    data: List[ProductResponse]  # list of products

    class Config:
        from_attributes = True