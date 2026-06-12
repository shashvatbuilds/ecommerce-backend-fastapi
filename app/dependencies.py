from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from fastapi import Depends,HTTPException,status
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

oauth_scheme =OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str =Depends(oauth_scheme),db:Session =Depends(get_db)):
    credential_exception =HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credentials")
    try:
        payload =jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])

        email:str =payload.get("sub")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    user =db.query(User).filter(User.email ==email).first()
    if not user:
        raise credential_exception
    return user

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user

    
    
