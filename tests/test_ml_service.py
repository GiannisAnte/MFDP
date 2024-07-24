import requests
import pytest
from tests.settings import test_users, test_data
import logging


api = 'http://localhost:8080/'
users = test_users()

@pytest.mark.parametrize(
    'token',
    [(user['token']) for user in users]
)
def test_check_task(token):
    '''запрос истории запросов юзера'''
    endpoint = '/task_history/'
    url = api + endpoint + token
    response = requests.get(url)
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert all(isinstance(task, dict) for task in tasks)

@pytest.mark.parametrize(
    'token',
    [(user['token']) for user in users]
)
def test_predict(token):
    endpoint = '/predict'
    url = api + endpoint + token
    data = test_data
    response = requests.get(url, json=data)
    assert response.status_code == 200
    assert response.json()['predicted_status'] in ('0', '1') 



