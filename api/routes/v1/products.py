from fastapi import APIRouter, Depends, Response, Request, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from db.session import get_db
from services.auth_service import request_otp, verify_otp_and_issue_tokens, refresh_tokens
from schemas.products import ProductCreate, ProductResponse, PaginatedProducts
from typing import List, Optional
from fastapi import Form
from fastapi import UploadFile, File
from services.product_service import create_product, get_products_paginated, get_product_by_id
from services.s3_service import s3_service



router = APIRouter(prefix="/v1/products", tags=["Products"])


from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(prefix="/v1/products", tags=["Products"])

@router.post("/", response_model=ProductResponse)
async def add_product(
    title: str = Form(...),
    one_liner: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    discounted_price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    dimensions: Optional[str] = Form(None),
    slug: Optional[str] = Form(None),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    # Upload images to S3
    image_links = []
    for image in images:
        try:
            await image.seek(0)
            url = await s3_service.upload_image(image)  # pass UploadFile directly
            image_links.append(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload {image.filename}: {str(e)}")

    # Build product data
    product_data = ProductCreate(
        title=title,
        one_liner=one_liner,
        description=description,
        price=price,
        discounted_price=discounted_price,
        category=category,
        subcategory=subcategory,
        dimensions=dimensions,
        slug=slug
    )

    # Create product in DB
    product = create_product(db, product_data=product_data, image_links=image_links)
    if not product:
        raise HTTPException(status_code=400, detail="Product creation failed")

    return product




@router.get("/", response_model=PaginatedProducts)
def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    sort_by: Optional[str] = Query(None, description="Field to sort by: price, created_at, title, discounted_price"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: asc or desc"),
):
    products, total = get_products_paginated(
        db=db,
        page=page,
        limit=limit,
        category=category,
        subcategory=subcategory,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,
        "data": products,
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to get a product by ID.
    Logic is delegated to helper function.
    """
    product = get_product_by_id(db, product_id)
    return product