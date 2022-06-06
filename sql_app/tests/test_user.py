
from sys import path
import random
import string
from fastapi.testclient import TestClient
from requests import Response

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

def get_user_json(user: UserCreate) -> dict:
    if type(user) != UserCreate: assert False
    new_user_json = {
        'email'   : user.email,
        'username': user.username,
        'password': user.password
    }
    return new_user_json

def post_request(response: Response):
    print(response.text)
    print(response.reason)

test_user : UserCreate = gen_new_user_dict()

common_headres = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def test_create_user():

    response = client.request("POST", "/users/reg",
                              json=get_user_json(test_user),
                              headers=common_headres)
    assert response.status_code == 200
    post_request(response)

def test_create_user_duplicate_fields():
    # Assumed that this test runs after test_create_user()
   
    response = client.request("POST", "/users/reg",
                                json=get_user_json(test_user),
                                headers=common_headres)
    assert response.status_code == 400
    post_request(response)


def test_obtain_user_token():
    headers = {
        'accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded'
    }
    data = f"grant_type=&username={test_user.username}&password={test_user.password}&scope=&client_id=&client_secret="
    response = client.request("POST", "/users/tkn", headers=headers, data=data)
    # if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type',''):
    #     print(response.json())

    assert response.status_code == 200
    post_request(response)


def test_reject_false_creds():
    headers = {
        'accept': 'application/json',
        'Content-type': 'application/x-www-form-urlencoded'
    }
    data = f"grant_type=&username={test_user.username}flaty&password=badpass{test_user.password}&scope=&client_id=&client_secret="
    response = client.request("POST", "/users/tkn", headers=headers, data=data)
    
    assert response.status_code == 401
    post_request(response)
    
def test_create_iot_entity():
    pass
