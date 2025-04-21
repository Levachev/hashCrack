import os
from threading import Thread
from time import sleep
from dotenv import load_dotenv, find_dotenv
from send_subscriber import SendSubscriber
from worker_service import WorkerService
from worker_controller import WorkerControler

sleep(5)
controller = WorkerControler()
load_dotenv(find_dotenv())
worker_service = WorkerService(controller)

send_subscriber = SendSubscriber()
thread = Thread(target = send_subscriber.start, args = (controller, ))
thread.start()
worker_service.start(os.environ.get('PORT'))