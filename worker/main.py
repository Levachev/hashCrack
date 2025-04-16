import os
from dotenv import load_dotenv, find_dotenv
from worker_service import WorkerService

service = WorkerService()
load_dotenv(find_dotenv())
service.start(os.environ.get('PORT'))