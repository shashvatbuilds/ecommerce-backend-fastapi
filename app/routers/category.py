from fastapi import APIRouter,Depends,HTTPException,status
from app.database import get_db
from app.models.category import Category
from sqlalchemy.orm import Session
from app.schemas.category import CategoryCreate,CategoryResponse,CategoryUpdate
from app.dependencies import admin_required
router =APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
    )
def create_category(
    create_data:CategoryCreate,
    db:Session =Depends(get_db),
    current_admin =Depends(admin_required)):
    existing_category =db.query(Category).filter(Category.name ==create_data.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    new_category =Category(
        name =create_data.name,
        description =create_data.description
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get(
    "/",
    response_model=list[CategoryResponse]
    )
def get_categories(db:Session =Depends(get_db)):
    categories =db.query(Category).all()

    return categories

@router.get(
    "/{id}",
    response_model=CategoryResponse
)
def get_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category

@router.put("/{id}",response_model=CategoryResponse)
def update_category(id:int,data:CategoryUpdate ,db: Session =Depends(get_db),current_admin =Depends(admin_required)):
    category =db.query(Category).filter(Category.id ==id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data =data.model_dump(
        exclude_unset=True
    )

    for key,value in update_data.items():
        setattr(category,key,value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{id}",status_code=status.HTTP_200_OK)
def delete_category(id:int,db: Session =Depends(get_db),current_admin =Depends(admin_required)):
    category =db.query(Category).filter(Category.id ==id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    db.delete(category)
    db.commit()
    return {"message":"category deleted successfully"}


