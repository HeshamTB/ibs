
from sys import path
import random
import string
from fastapi.testclient import TestClient

from ..main import app
from ..schemas import UserCreate


MAX_ASCII = 255
RAND_CHAR_SET = string.ascii_letters

client = TestClient(app)


def gen_rand_str(size: int) -> str:
    return ''.join(random.choice(RAND_CHAR_SET) for x in range(size))

def gen_new_user_dict() -> UserCreate:
    noune = gen_rand_str(16)
    new_user = UserCreate(email=f"testuser{noune}@mail.none",
                         username=f"testuser{noune}",
                         password=noune)
    return new_user

test_user : UserCreate = gen_new_user_dict()

common_headres = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def test_create_user():

    new_user_json = {
        "email"   : test_user.email,
        "username": test_user.username,
        "password": test_user.password
    }
    response = client.request("POST", "/users/reg",
                              json=new_user_json,
                              headers=common_headres)
    assert response.status_code == 200

def test_create_user_duplicate_fields():
    # Assumed that this test runs after test_create_user()
    new_user_json = {
        "email"   : test_user.email,
        "username": test_user.username,
        "password": test_user.password
    }
    response = client.request("POST", "/users/reg",
                                json=new_user_json,
                                headers=common_headres)
    assert response.status_code == 400

def test_create_iot_entity():
    pass
