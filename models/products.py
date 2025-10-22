from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from db.base import Base


# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255), nullable=False)
#     slug = Column(String(255), unique=True, index=True, nullable=False)
#     one_liner = Column(String(255), nullable=True)
#     description = Column(Text, nullable=True)
#     image_links = Column(ARRAY(String), nullable=True)  
#     price = Column(Float, nullable=False)
#     discounted_price = Column(Float, nullable=True)
#     category = Column(String(100), index=True, nullable=True)
#     subcategory = Column(String(100), index=True, nullable=True)
#     dimensions = Column(String(100), nullable=True)  # e.g., "10x20x15 cm"  should include all 3
#     is_active = Column(Boolean, default=True, nullable=False)

#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     analytics = relationship("ProductAnalytics", back_populates="product", uselist=False)

# #cateogry apis
# # top 4 products for each caregorry api



# class ProductAnalytics(Base):
#     __tablename__ = "product_analytics"

#     id = Column(Integer, primary_key=True, index=True)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
#     view_count = Column(Integer, default=0, nullable=False)
#     purchase_count = Column(Integer, default=0, nullable=False)
#     last_purchased_at = Column(DateTime(timezone=True), nullable=True)
#     rating = Column(Float, default=0.0)
#     review_count = Column(Integer, default=0)
#     stock_count = Column(Integer, default=0)
#     wishlist_count = Column(Integer, default=0)

#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

#     # Relationship to Product
#     product = relationship("Product", back_populates="analytics")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    one_liner = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category_rel")


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory_rel")




class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    one_liner = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_links = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Category relationships
    category_id = Column(Integer, ForeignKey("categories.id"))
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category_rel = relationship("Category", back_populates="products")
    subcategory_rel = relationship("SubCategory", back_populates="products")
    analytics = relationship("ProductAnalytics", back_populates="product", uselist=False)
    dimensions_rel = relationship("ProductDimension", back_populates="product", cascade="all, delete-orphan")


# ========================
# PRODUCT DIMENSIONS (variant-specific pricing)
# ========================

class ProductDimension(Base):
    __tablename__ = "product_dimensions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    dimension = Column(String(100), nullable=False)  # e.g., "S", "M", "L" or "10x20x15 cm"
    price = Column(Float, nullable=False)
    discounted_price = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="dimensions_rel")


# ========================
# PRODUCT ANALYTICS
# ========================

class ProductAnalytics(Base):
    __tablename__ = "product_analytics"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    last_purchased_at = Column(DateTime(timezone=True))
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    stock_count = Column(Integer, default=0)
    wishlist_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="analytics")