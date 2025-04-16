import uuid
from time import sleep

import pika


class Publisher(object):
    def __init__(self):
        amqp_url = 'amqp://guest:guest@rabbitmq?heartbeat=65535&blocked_connection_timeout=65535'
        url_params = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(url_params)

        self.channel = self.connection.channel()
        self.corr_id = None

    def call(self, msg):
        self.corr_id = str(uuid.uuid4())

        while True:
            sleep(0)
            try:
                sleep(6)
                self.channel.basic_publish(
                    exchange="",
                    routing_key="rpc_queue2",
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        correlation_id=self.corr_id,
                    ),
                    body=msg,
                )
                return
            except Exception as e:
                while True:
                    sleep(2)
                    try:
                        amqp_url = 'amqp://guest:guest@rabbitmq?heartbeat=65535&blocked_connection_timeout=65535'
                        url_params = pika.URLParameters(amqp_url)
                        self.connection = pika.BlockingConnection(url_params)

                        self.channel = self.connection.channel()
                        break
                    except Exception as e2:
                        print("cannot connect to rabbitmq")