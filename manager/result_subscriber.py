import json
from threading import Thread
from time import sleep

import pika

class ResultSubscriber:
    def start(self, manager):
        amqp_url = 'amqp://guest:guest@rabbitmq?heartbeat=65535&blocked_connection_timeout=65535'
        url_params = pika.URLParameters(amqp_url)
        connection = pika.BlockingConnection(url_params)
        channel = connection.channel()
        channel.queue_declare(queue="rpc_queue2")

        def logic(body):
            jsn = body.decode()
            data = json.loads(jsn)
            manager.update_request_data(data.get("requestId"), data.get('data'))
            return 'ok'

        def on_request(ch, method, props, body):

            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!get in subscriber")
            response = logic(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("after ack")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="rpc_queue2", on_message_callback=on_request)

        print(" [x] Awaiting RPC requests")
        while True:
            sleep(4)
            try:
                print("try to start consuming")
                channel.start_consuming()
            except Exception as e:
                print("exception while consuming")
                while True:
                    sleep(2)
                    try:
                        amqp_url = 'amqp://guest:guest@rabbitmq?heartbeat=65535&blocked_connection_timeout=65535'
                        url_params = pika.URLParameters(amqp_url)
                        connection = pika.BlockingConnection(url_params)
                        channel = connection.channel()
                        channel.queue_declare(queue="rpc_queue2")

                        channel.basic_qos(prefetch_count=1)
                        channel.basic_consume(queue="rpc_queue2", on_message_callback=on_request)
                        break
                    except Exception as e2:
                        print("cannot connect to rabbitmq")
