import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login') # this is the login endpoint in auth.py

#SECRET_KEY
SECRET_KEY = settings.secret_key
#ALGORITHM: HSA256
ALGORITHM = settings.algorithm
#Expiration Time
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # timezone utc ensured the country
    to_encode.update({"exp": expire})

    # encoded = jwt.encode({"some": "payload"}, key, algorithm="HS256") - docs reference
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:
        # jwt.decode(encoded, key, algorithms="HS256") # Decode Fastapi reference
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # id:str = payload.get("user_id")
        id = str(payload.get("user_id"))

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)

    except InvalidTokenError:
        raise credentials_exception

    return token_data


def get_current_user(token: str=Depends(oauth2_scheme), db: Session=Depends(database.get_db)): # so this basically authenticates the user, and we can pass this in routes which we can access when user is logged in
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", 
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id==token.id).first()

    return user
