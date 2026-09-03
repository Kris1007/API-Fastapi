from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter # imports router
from .. import models, schemas, oauth2
import time
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import engine, get_db
from typing import Optional, List

router = APIRouter(
    prefix="/posts", # simplifies the route to use / instead of /posts
    tags=['Posts'] # groups the docs under the section Posts
)

@router.get("/", response_model = List[schemas.PostOut]) # the / is interprested as /posts as you can see in prefix in APIRouter
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str]=""): # default limit = 10 posts
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # print(posts)

    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # to ensure that owner sees his post only
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() # offset is used to skip

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #post votes, SQL Alchemy left Inner Join by default, isouter makes it LEFT OUTER JOIN

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published)) #sanitize inputs
    # new_post = cursor.fetchone()
    # conn.commit()

    # print(current_user.id)
    # print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.dict()) # to avoid manually typing post.title, post.content, etc.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/latest", response_model = schemas.PostOut)
def get_latest_post(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1""")
    # post = cursor.fetchall()

    # post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc()).first() 

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return post


@router.get("/{id}", response_model = schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): #provide id requirement
    # cursor.execute("""SELECT * FROM posts WHERE id= %s""", (str(id))) # need to convert id to string to execute it
    # post = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.id==id).first() # only searches for one query result and here there will be only one query results because id is unique
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first() 

    if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"post with id: {id} was not found")
    return posts


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # deleting post
    # find index in array that has required ID
    # my_posts.pop(index)
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()

    deleted_post_query = db.query(models.Post).filter(models.Post.id==id)
    deleted_post = deleted_post_query.first()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")

    deleted_post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""", (post.title, post.content, post.published, (str(id),)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    updated_post_query = db.query(models.Post).filter(models.Post.id==id)
    updated_post = updated_post_query.first()

    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    if updated_post.owner_id != current_user.id:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")

    updated_post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    return updated_post
