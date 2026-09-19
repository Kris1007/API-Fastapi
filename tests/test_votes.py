import pytest
from app import models

# we put this fixture here because it is not really required in any other function
@pytest.fixture()
def test_vote(test_posts, session, test_user):
   new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
   session.add(new_vote)
   session.commit()
   

def test_vote_on_post(authorized_client, test_posts, test_user2):
   res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
   assert res.status_code == 201

def test_votes_twice_post(authorized_client, test_posts, test_vote):
   res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
   assert res.status_code == 409

def test_delete_vote(authorized_client, test_posts, test_vote):
   res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
   assert res.status_code == 201

def test_delete_vote_not_exist(authorized_client, test_posts):
   res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
   assert res.status_code == 404

def test_vote_post_non_exists(authorized_client, test_posts):
   res = authorized_client.post("/vote/", json={"post_id": 80000, "dir": 1})
   assert res.status_code == 404 

def test_vote_unauthorized_user(client, test_posts):
   res = client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
   assert res.status_code == 401