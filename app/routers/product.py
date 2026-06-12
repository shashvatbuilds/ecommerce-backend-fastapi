from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.dependencies import admin_required
import os
import uuid
from fastapi import UploadFile, File

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post(
    "/create_product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_required)
):
    categories = db.query(Category).filter(
        Category.id.in_(product_data.category_ids)
    ).all()

    if len(categories) != len(product_data.category_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more category IDs are invalid"
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        categories=categories
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products(
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.offset(skip).limit(limit).all()

    return products

@router.get(
    "/{id}",
    response_model=ProductResponse
)
def get_product(
    id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product

@router.put(
    "/update/{id}",
    response_model=ProductResponse
)
def update_product(
    id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_required)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids")

        categories = db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()

        if len(categories) != len(category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more category IDs are invalid"
            )

        product.categories = categories

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product

@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(admin_required)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }

@router.post(
    "/{id}/upload-image",
    response_model=ProductResponse
)
def upload_product_image(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin=Depends(admin_required)
):
    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WEBP images are allowed"
        )

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    upload_path = f"uploads/products/{unique_filename}"

    with open(upload_path, "wb") as buffer:
        buffer.write(file.file.read())

    product.image_url = f"/uploads/products/{unique_filename}"

    db.commit()
    db.refresh(product)

    return product
