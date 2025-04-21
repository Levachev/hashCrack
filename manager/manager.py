# This code is a translation of a Node.js JavaScript application.
import os
from dotenv import load_dotenv, find_dotenv
import json
import requests
import schedule
import time
from queue import Queue
import threading

from status import Status
from repo import Repo
from recv_msg import Request
from publisher import Publisher


class Manager:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.alphabet = os.environ.get('ALPHABET')
        self.timeout = int(os.environ.get('TIMEOUT'))
        self.workers_count = int(os.environ.get('WORKERS_COUNT'))
        self.workers_host = os.environ.get('WORKERS_HOST')
        self.workers_port = int(os.environ.get('WORKERS_PORT'))
        self.free_workers = self.workers_count
        self.requests = {}
        self.max_queue_size = int(os.environ.get('QUEUE_SIZE'))
        self.queue = Queue()
        self.free_workers_lock = threading.Lock()
        self.send_publisher = Publisher()
        self.repo = Repo()
        self.workerStatus = [self.workers_count]
        for i in range(self.workers_count):
            self.workerStatus.append(True)

        thread = threading.Thread(target=self.schedule_actions, args=())
        thread.start()

    def check_in_progress_requests(self):
        print("checking in_progress requests")

        requests_past = self.repo.fetch_all()
        print("requests past", requests_past.collection.count_documents({}))
        for req in requests_past:
            if req['status'] == Status["InProgress"]:
                print("updating request", req['_id'])
                self.handle_request({
                    'id': req['_id'],
                    'hash': req['hash'],
                    'maxLength': req['maxLength']
                })

    def schedule_actions(self):
        schedule.every(10).seconds.do(self.healthcheck)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def healthcheck(self):
        for i in range(1, self.workers_count + 1):
            url = f"{self.workers_host}{i}:{self.workers_port}"
            try:
                res = requests.get(f"{url}/internal/api/worker/healthcheck")
                if not res.ok:
                    self.workerStatus[i] = False
                else:
                    self.workerStatus[i] = True
            except Exception as e:
                self.workerStatus[i] = False
                print(f'Failed to get progress for {url}', " ", str(e))
        print("workers alive: ", str(self.workerStatus))

    def handle_request(self, request):
        if self.queue.qsize() >= self.max_queue_size:
            return None

        request_id = str(request['id'])
        req = Request(request_id, request['hash'], request['maxLength'])
        self.repo.save_request(req)
        print(f'New request {request_id}')
        print(f'Request h={req.hash} maxLen={req.max_length}')

        self.requests[request_id] = req
        self.queue.put(req)

        self.schedule_tasks()
        return request_id

    def has_request(self, request_id):
        return request_id in self.requests

    def get_request_status(self, request_id):
        print(f'Getting request status for {request_id}')
        req = self.requests.get(request_id)

        print("req.in_progress(): ", req.in_progress())
        if req.in_progress():
            progress = self.fetch_progress()
            print(f'Send status for {request_id}')
            return req.get_status_with_progress(progress)
        else:
            return req.get_status()

    def update_request_data(self, request_id, data):
        print(f'Updating request {request_id}')
        with self.free_workers_lock:
            self.free_workers += 1

            req = self.requests.get(request_id)
            if req is None:
                all = self.repo.fetch_all()
                for req1 in all:
                    if req1['_id'] == request_id:
                        req2 = Request(request_id, req1['hash'], req1['maxLength'])
                        self.requests[request_id] = req2
                        break

            req = self.requests.get(request_id)
            req.add_data(data, self.repo)

            print("stat: ", req.status)

            print(self.free_workers)
            print(self.workers_count)

            if self.free_workers >= self.workers_count:
                req.complete(self.repo)
                print(f'Request completed {request_id}')
            threading.Timer(req.timer_id, req.complete).cancel()
            self.schedule_tasks()

    def schedule_tasks(self):
        if self.queue.qsize() == 0 or self.free_workers < self.workers_count:
            return

        req = self.queue.get()
        print(f'Start processing {req.id}')
        self.send_tasks(req)

        req.timer_id = threading.Timer(self.timeout, self.request_timeout_expired, [req.id])
        req.timer_id.start()

    def fetch_progress(self):
        current = 0
        total = 0

        for i in range(1, self.workers_count + 1):
            url = f"{self.workers_host}{i}:{self.workers_port}"
            try:
                res = requests.get(f"{url}/internal/api/worker/hash/crack/progress")
                if not res.ok:
                    continue
                body = res.json()
                current += body['processed']
                total += body['count']
            except Exception as e:
                print(f'Failed to get progress for {url}',  " ", str(e))

        percent = (current / total) * 100 if total > 0 else 0
        print(f'Progress {current}/{total} {percent}%')
        return percent

    def fetch_progress2(self):
        current = 0
        total = 0

        for i in range(1, self.workers_count + 1):
            print("ask progress for ", i)
            ret = self.send_publisher.call('2')
            if(ret == None):
                continue
            ret = ret.decode()
            ret = ret.replace("\'", "\"")
            data = json.loads(ret)
            current += data.get('processed')
            total += data.get('count')
            print("ret: ", ret)

        percent = (current / total) * 100 if total > 0 else 0
        print(f'Progress {current}/{total} {percent}%')
        return percent

    def request_timeout_expired(self, request_id):
        req = self.requests.get(request_id)
        req.set_error_status(self.repo)
        print(f'Request timeout expired {request_id}')

    def send_tasks(self, req):
        total = self.perms_count(len(self.alphabet), req.max_length)
        count_per_task = total // self.workers_count

        task = {
            'requestId': req.id,
            'hash': req.hash,
            'alphabet': self.alphabet,
            'start': 0,
            'count': count_per_task
        }

        for i in range(1, self.workers_count):
            self.send_task2(task)
            task['start'] += count_per_task

        task['count'] = total - task['start']
        self.send_task2(task)

    def send_task(self, worker, task):
        url = f"{self.workers_host}{worker}:{self.workers_port}"
        try:
            res = requests.post(f"{url}/internal/api/worker/hash/crack/task", json=task, headers={'Content-Type': 'application/json;charset=utf-8'})
            print(f'{worker} task sent')
            with self.free_workers_lock:
                self.free_workers -= 1
                print(f'free_workers {self.free_workers}')
        except Exception as e:
            print(e)

    def send_task2(self, task):
        ret = self.send_publisher.call(json.dumps(task))
        print("ret: ", ret)
        with self.free_workers_lock:
            self.free_workers -= 1

    def perms_count(self, n, k):
        count = 0
        for i in range(1, k + 1):
            count += n ** k
        return count