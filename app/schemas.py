from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Creating models for each and every request

# Schema

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

# this class is created to see what responses user can see, it is called in routes by responseModel = schemas.Post() in main.py
class Post(PostBase): #inheritance from PostBase
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut # return the pydantic model

    # if the data returned is not dictionary the following takes it as dictionary
    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post # in example.py we can see it returns a dictionary instead 
               # of JSON having posts, and second post after : is the Post class above 
               #so that it takes its property and becomes a json
    votes: int

    class Config:
            orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: int = Field(ge=0, le=1)
