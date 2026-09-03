from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm  # using this we can have the post request of login
                                                               # in form of form which uses username instead of email
                                                               # and we can provide data in form of key value pair form
                                                               # instead of json
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, utils, oauth2, schemas

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    # OAuth2PasswordRequestForm return username, password only as it doesn't provided email we use username instead
    #{
    #    "username": "asdf",
    #    "password": "bla"
    #}
    # so basically: user_credentials.username
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # Create a JWT token and then return the token

    access_token = oauth2.create_access_token(data={"user_id": user.id}) # provide payload, information about user, more info can be added

    return {"access_token":access_token, "token_type": "bearer"}