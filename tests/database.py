from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app.database import get_db, Base
from app.config import settings
from alembic import command

# Setting up test db
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db # references the new instance to
                                                   # previous get_db method so that we don't have
                                                   # to reinitialize routes or add override_get_db
                                                   # functionility in all of them

# ** we can create a fixture which we can use inside another fixture
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine) # drops all the tables so same test
                                        # can be ran multiple times (can see the tables if we pass drop_all above create_all)
    Base.metadata.create_all(bind=engine) # created the tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture() # creating fixture for test client
def client(session): # client calls session fixture before it runs
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # If using alembic
    #command.upgrade("head")
    # run our code before we run out test
    # run our code after out test finishes
    #command.downgrade("base")