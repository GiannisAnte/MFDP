import pika
import uuid
import json
from worker_conn import get_connection


class RpcClient(object):

    def __init__(self):
        self.connection = get_connection()

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body = message)
        try:
            while self.response is None:
                self.connection.process_data_events(time_limit=1)  #таймаут обработки
            print('Return success response')
            return json.loads(self.response)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None 