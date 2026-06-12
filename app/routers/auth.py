from fastapi import APIRouter,HTTPException,status,Depends
from app.schemas.user import UserCreate,UserResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.hashing import hash_password,verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.jwt_handler import create_access_token
from app.dependencies import get_current_user

router =APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",
    response_model =UserResponse,
    status_code =status.HTTP_201_CREATED
)
def register_user(
    user_data:UserCreate,
    db :Session =Depends(get_db)
):
    existing_user =db.query(User).filter(User.email==user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Already Exist")
    
    new_user =User(
        name =user_data.name,
        email =user_data.email,
        hashed_password =hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(
    form_data:OAuth2PasswordRequestForm =Depends(),
    db:Session =Depends(get_db)):
    user =db.query(User).filter(User.email ==form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    if not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    
    token =create_access_token({"sub":user.email,"role":user.role})

    return {
        "access_token":token,
        "token_type":"bearer"
    }

@router.get("/me",response_model=UserResponse)
def get_me(current_user:User =Depends(get_current_user)):
    return current_user
