from slugify import slugify
from sqlalchemy.orm import Session
from models.products import Product, ProductAnalytics
from schemas.products import ProductCreate
from datetime import datetime
from sqlalchemy import desc


def create_product(db: Session, product_data: ProductCreate, image_links: list):
    """
    Create a new product with unique slug and proper handling of list fields.
    """
    base_slug = slugify(product_data.title)
    slug = base_slug
    counter = 1

    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    db_product = Product(
        title=product_data.title.strip(),
        slug=slug,
        one_liner=product_data.one_liner,
        description=product_data.description,
        image_links=image_links or [],  
        price=product_data.price,
        discounted_price=product_data.discounted_price,
        category=product_data.category,
        subcategory=product_data.subcategory,
        dimensions=product_data.dimensions,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from typing import Optional, Tuple, List
from fastapi import HTTPException, status

SORTABLE_FIELDS = {
    "price": Product.price,
    "discounted_price": Product.discounted_price,
    "created_at": Product.created_at,
    "title": Product.title,
    # Analytics fields
    "view_count": ProductAnalytics.view_count,
    "purchase_count": ProductAnalytics.purchase_count,
    "rating": ProductAnalytics.rating,
    "review_count": ProductAnalytics.review_count,
    "stock_count": ProductAnalytics.stock_count,
    "wishlist_count": ProductAnalytics.wishlist_count,
}

def get_products_paginated(
    db: Session,
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> Tuple[List[Product], int]:
    """
    Fetch paginated products with optional filters, sorting, and analytics included.
    """
    query = db.query(Product).options(joinedload(Product.analytics))

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if subcategory:
        query = query.filter(Product.subcategory.ilike(f"%{subcategory}%"))
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))

    # Apply sorting if valid
    if sort_by in SORTABLE_FIELDS:
        column = SORTABLE_FIELDS[sort_by]
        if sort_order.lower() == "desc":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return products, total



def get_product_by_id(db: Session, product_id: int):
    """
    Fetch a product by ID, increase its view count, and return it.
    Handles missing records and database errors gracefully.
    """
    try:
        # Fetch product
        product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active == True)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

        # Fetch analytics record for this product
        analytics = (
            db.query(ProductAnalytics)
            .filter(ProductAnalytics.product_id == product_id)
            .first()
        )

        # Create analytics row if it doesn't exist
        if not analytics:
            analytics = ProductAnalytics(product_id=product_id, view_count=1)
            db.add(analytics)
        else:
            analytics.view_count += 1
            analytics.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(product)

        return product

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while fetching product: {str(e)}",
        )
