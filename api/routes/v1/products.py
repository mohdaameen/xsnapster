from fastapi import APIRouter, Depends, Response, Request, HTTPException, status, Body
from sqlalchemy.orm import Session
from db.session import get_db
from services.auth_service import request_otp, verify_otp_and_issue_tokens, refresh_tokens
from schemas.products import ProductCreate, ProductResponse
from typing import List, Optional
from fastapi import Form
from fastapi import UploadFile, File
from services.product_service import create_product
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

