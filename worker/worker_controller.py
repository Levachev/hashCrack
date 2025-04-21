import os
import threading
import time

import schedule
from dotenv import load_dotenv, find_dotenv
import json
import requests

from brute_force import HashBruteForce
from task_progress import TaskProgress, TaskProgressSize
from publisher import Publisher


class WorkerControler:
    buffer = bytearray(TaskProgressSize)
    taskProgress = TaskProgress(buffer)
    currentTask = {
        "requestId": "",
        "hash": "",
        "alphabet": "",
        "start": 0,
        "count": 0
    }
    completed = True

    def __init__(self):
        load_dotenv(find_dotenv())
        self.managerUrl = os.environ.get("MANAGER_URL")
        self.buffer = bytearray(TaskProgressSize)
        self.taskProgress = TaskProgress(self.buffer)
        self.currentTask = {
            "requestId": "",
            "hash": "",
            "alphabet": "",
            "start": 0,
            "count": 0
        }
        self.completed = True
        self.send_publisher = Publisher()
        thread = threading.Thread(target=self.schedule_actions, args=())
        thread.start()

    def schedule_actions(self):

        schedule.every(10).seconds.do(self.print_pregress)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def processTask(self, task):
        if not self.completed:
            return False

        print(f"Processing task {task['requestId']}")
        print(f"Range start={task['start']}, count={task['count']}")

        self.currentTask = task
        self.completed = False
        self.taskProgress.current = 0
        hash = HashBruteForce()
        l = lambda: setattr(self.taskProgress, 'current', self.taskProgress.current + 1)

        result = hash.crackHash(self.currentTask, l)

        self.completed = True
        self.__sendResult2(result)
        print("result: ", result)
        return True

    def getProgress(self):
        print("getProgress")
        progress = {
            "processed": self.taskProgress.current,
            "count": self.currentTask.get("count")
        }
        percent = int((progress["processed"] / progress["count"]) * 100) if progress["count"] else 0
        print(f"Progress {progress['processed']}/{progress['count']} {percent}%")
        return progress

    def __sendResult(self, result):
        print(f"Found {len(result)} words")
        try:
            response = requests.patch(f"{self.managerUrl}/internal/api/manager/hash/crack/request",
                                      headers={'Content-Type': 'application/json;charset=utf-8'},
                                      data=json.dumps({
                                          "requestId": self.currentTask["requestId"],
                                          "data": result
                                      }))
        except Exception as reason:
            print(reason)
        else:
            print("Result sended")

    def __sendResult2(self, result):
        data = json.dumps({
            "requestId": self.currentTask["requestId"],
            "data": result
        })
        self.send_publisher.call(data)

    def print_pregress(self):
        progress = {
            "processed": self.taskProgress.current,
            "count": self.currentTask.get("count")
        }
        percent = int((progress["processed"] / progress["count"]) * 100) if progress["count"] else 0
        print(f"Progress {progress['processed']}/{progress['count']} {percent}%")