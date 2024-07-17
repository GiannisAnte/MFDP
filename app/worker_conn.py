import os
import pika
from pika import BlockingConnection
from dotenv import load_dotenv
import time

# путь к .env файлу
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))
load_dotenv(env_path)

connection_params = pika.ConnectionParameters(
    host=os.environ['RABBIT_HOST'], 
    port=5672, 
    virtual_host='/',   # Виртуальный хост (обычно '/')
    credentials=pika.PlainCredentials(
        username=os.environ['RABBITMQ_DEFAULT_USER'],
        password=os.environ['RABBITMQ_DEFAULT_PASS'],
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)


def get_connection() -> BlockingConnection:
    # return pika.BlockingConnection(connection_params)
    retries = 3
    for att in range(retries):
        try:
            print(f"Сonnection {att + 1}/{retries}")
            connection = pika.BlockingConnection(connection_params)
            return connection  # Возвращаем соединение при успешном подключении
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error: {e}")
            if att < retries - 1:
                print("Try again in 5 seconds")
                time.sleep(5)
            else:
                print("Connection attempts ended, exit from connection")
                raise

