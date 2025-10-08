from slugify import slugify
from sqlalchemy.orm import Session
from models.products import Product
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



def get_all_products(
    db: Session,
    category: str = None,
    subcategory: str = None,
    is_active: bool = True,
    sort_by: str = None,
    skip: int = 0,
    limit: int = 20,
):
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if subcategory:
        query = query.filter(Product.subcategory == subcategory)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "rating":
        query = query.join(Product.analytics).order_by(desc(Product.analytics.rating))
    elif sort_by == "popularity":
        query = query.join(Product.analytics).order_by(desc(Product.analytics.purchase_count))
    else:
        query = query.order_by(Product.created_at.desc())

    return query.offset(skip).limit(limit).all()
