import pika
import pandas as pd
import pickle
import json
from worker_conn import connection_params
import joblib

# Загрузка модели
with open("files_for_ml/diabet_rfc.pkl", 'rb') as file:
        global model
        model = joblib.load(file)

# Установка соединения
connection = pika.BlockingConnection(connection_params)

# Создание канала
channel = connection.channel()

queue_name = 'rpc_queue'

# Создание очереди
channel.queue_declare(queue=queue_name)


# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    # Обработка полученного запроса
    message_body = json.loads(body)
    input_df = pd.DataFrame(message_body, index=[0])
    result = model.predict(input_df)[0]
    response = {'predicted_status': str(result)}

    # Отправка ответа в качестве ответа в канал
    # c уникальным идентификатором
    response_channel = connection.channel()
    response_channel.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response),
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
            )
    )
    response_channel.close()
    # Ручное подтверждение обработки сообщения
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    # Подписка на очередь и установка обработчика сообщений
    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=False)
    # Начало потребления сообщений
    print('In working')
    channel.start_consuming()


if __name__ == '__main__':
    start_worker()
