import pytest
from app import schemas
# conftest.py automatically have access to test files
import jwt
from app.config import settings

@pytest.fixture
def test_user(client):
    user_data = {"email": "krishna@gmail.com",
                 "password": "password"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

# def test_root(client):
#     res = client.get("/")
#     print(res.json().get('message'))
#     assert(res.json().get('message')) == 'Hi Everyone! Welcome to this amazing API buddy'
#     assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})
    new_user = schemas.UserOut(**res.json()) # follows the userOut schema, ** means unpack to dictionary
    assert new_user.email == "hello123@gmail.com" # userOut schema in get
    assert res.status_code == 201

# each and every test should be independent and not depend on each other
def test_login_user(client, test_user):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']}
    )
    login_res = schemas.Token(**res.json())
    # jwt.decode(encoded, key, algorithms="HS256") # Decode Fastapi reference
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    
    # id:str = payload.get("user_id")
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "password", 403),
    ("krishna@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password", 422),
    ("krishna@gmail.com", None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid Credentials'
 