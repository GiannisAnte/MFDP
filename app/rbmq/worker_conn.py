import os
import pika
from pika import BlockingConnection
from dotenv import load_dotenv

# путь к .env файлу
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '.env'))
load_dotenv(env_path)

connection_params = pika.ConnectionParameters(
    host=os.environ['RABBITMQ_HOST'],  # Замените на адрес вашего RabbitMQ сервера
    port=os.environ['RABBITMQ_PORT'],  # Замените на адрес вашего RabbitMQ сервера
    virtual_host='/',   # Виртуальный хост (обычно '/')
    credentials=pika.PlainCredentials(
        username=os.environ['RABBITMQ_DEFAULT_USER'],  # Имя пользователя по умолчанию
        password=os.environ['RABBITMQ_DEFAULT_PASS'],  # Имя пользователя по умолчанию
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)


def get_connection() -> BlockingConnection:
    return pika.BlockingConnection(connection_params)
