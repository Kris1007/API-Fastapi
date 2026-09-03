from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter # imports router
from .. import models, schemas, utils
import time
from sqlalchemy.orm import Session
from ..database import engine, get_db

router = APIRouter(
    prefix="/users", # simplifies the route to use / instead of /users
    tags=['Users'] # groups the docs under the section Users
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    user_data = user.dict()
    user_data["password"] = utils.hash(
        user_data["password"]
    )

    # new_user = models.User(**user.dict()) # to avoid manually typing post.title, post.content, etc.
    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user   


@router.get('/{id}', response_model= schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")

    return user
