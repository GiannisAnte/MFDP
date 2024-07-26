import requests
import pytest
from tests.settings import test_users


api = 'http://localhost:8080/'
users = test_users()

def test_list_of_all_users():
    '''Тест получения списка всех юзеров'''
    endpoint = '/user/users'
    url = api + endpoint
    response = requests.get(url)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert all(isinstance(user, dict) for user in users)

    for user in users:
        assert 'id пользователя' in user
        assert 'имя пользователя' in user
        assert 'email' in user
        assert 'пароль' in user

def test_list_of_all_transactions():
    '''Тест получения списка всех транзакций'''
    endpoint = '/user/transaction_history'
    url = api + endpoint
    response = requests.get(url)
    assert response.status_code == 200
    transactions = response.json()
    assert isinstance(transactions, list)
    assert all(isinstance(transaction, dict) for transaction in transactions)

    for transaction in transactions:
        assert 'user_id' in transaction
        assert 'amount' in transaction
        assert 'transaction_id' in transaction
        assert 'transaction_type' in transaction

def test_list_of_all_tasks():
    '''Тест получения списка всех запросов'''
    endpoint = '/user/tasks_history'
    url = api + endpoint
    response = requests.get(url)
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert all(isinstance(task, dict) for task in tasks)

    for task in tasks:
        assert 'action_id' in task
        assert 'amount' in task
        assert 'input_data' in task
        assert 'response' in task and response
        assert isinstance(task['input_data'], str)
        assert task['response'] in ('0', '1')


@pytest.mark.parametrize(
    'token',
    [(user['token']) for user in users]
)
def test_check_balance(token):
    '''Тест получения баланса юзера'''
    endpoint = '/user/balance/'
    url = api + endpoint
    response = requests.get(url, 
                            params={'token': token})
    assert response.status_code == 200
    balance = response.json()
    assert type(balance) == float

@pytest.mark.parametrize(
    'token',
    [(user['token']) for user in users]
)
def test_check_add(token):
    '''Тест пополнения баланса'''
    endpoint = '/user/coin/'
    url = api + endpoint
    amount = 10
    response = requests.get(url, 
                            params={'token': token, "amount": amount})
    assert response.status_code == 200
    assert response.json() == {"message": "Coin added to user"}


@pytest.mark.parametrize(
    'token',
    [(user['token']) for user in users]
)
def test_check_history(token):
    '''Тест запроса истории транзакций юзера'''
    endpoint = '/user/transactions/'
    url = api + endpoint + token
    response = requests.get(url)
    assert response.status_code == 200
    histories = response.json()
    assert isinstance(histories, list)
    assert all(isinstance(history, dict) for history in histories)


