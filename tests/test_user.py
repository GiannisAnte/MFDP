import requests
import pytest
from tests.settings import test_users


api = 'http://localhost:8080/'
users = test_users()

#параметры для функции
@pytest.mark.parametrize(
        ['username', 'email', 'password'],
        [
            (user['username'], user['email'], user['password'])
            for user in users
        ]
    )
def test_signup(username, email, password):
    '''тест регистрации'''
    endpoint = '/user/signup'
    url = api + endpoint
    response = requests.post(url,
                            params={"username": username,
                                    "email": email,
                                    "password": password})
    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered!"}



@pytest.mark.parametrize(
        ['username', 'password'],
        [
            (user['username'], user['password'])
            for user in users
        ]
    )
def test_signin(username, password):
    '''тест авторизации'''
    endpoint = '/user/signin'
    url = api + endpoint
    response = requests.post(url,
                            params={"username": username,
                                    "password": password})
    response_json = response.json()
    assert response_json["token_type"] == "Bearer"
    assert "access_token" in response_json and "token_type" in response_json
    