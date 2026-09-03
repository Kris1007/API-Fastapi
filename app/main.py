from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

# This command creates the tables from models.py whenever the fastapi is running 
# models.Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = ["*"] # wildcard works on every website

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# while True:

#     try:
#         conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username, password=settings.database_password,
#         cursor_factory=RealDictCursor)
#         cursor = conn.cursor() # to execute sql statements
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2)


app.include_router(post.router) # grabs router in user file and import all their routes, it goes to routers folder identify the post route
app.include_router(user.router) # #grabs router in user file and import all their routes, it goes to routers folder identify the user route
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    return {"message": "Welcome to this amazing API"}




# 11:00 minutes
                 