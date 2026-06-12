from app.config import settings
from datetime import datetime,timezone,timedelta
from jose import jwt

def create_access_token(data:dict)->str:
    encode_data =data.copy()
    expire_time =datetime.now(timezone.utc) +timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp":expire_time})
    token =jwt.encode(encode_data,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return token