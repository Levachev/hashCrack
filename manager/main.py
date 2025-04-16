from manager_service import ManagerService
import os
from dotenv import load_dotenv, find_dotenv

manager_service = ManagerService()
load_dotenv(find_dotenv())
manager_service.start(os.environ.get('MANAGER_PORT'))