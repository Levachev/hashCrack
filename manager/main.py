from threading import Thread
from time import sleep

from manager import Manager
from result_subscriber import ResultSubscriber
from manager_service import ManagerService
import os
from dotenv import load_dotenv, find_dotenv

sleep(5)
manager = Manager()

manager_service = ManagerService(manager)

load_dotenv(find_dotenv())

answ_consumer = ResultSubscriber()
print("run subscriber")
thread = Thread(target = answ_consumer.start, args = (manager, ))
thread.start()
sleep(5)
manager.check_in_progress_requests()
manager_service.start(os.environ.get('MANAGER_PORT'))