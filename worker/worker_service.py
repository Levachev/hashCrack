from threading import Thread

from flask import Flask, request, jsonify, Response
from worker_controller import WorkerControler

class WorkerService:
    def __init__(self):
        self.app = Flask(__name__)
        self.controller = WorkerControler()

        # Configure the app to parse JSON requests
        # Equivalent to app.use(express.json()) in JavaScript
        @self.app.route("/internal/api/worker/hash/crack/task", methods=["POST"])
        def handle_task():
            # Check if the request body exists; if not, return a 400 status code
            data = request.get_json()
            if not data:
                return Response(status=400)

            # Construct the task object with required properties
            task = {
                "requestId": data.get("requestId"),
                "hash": data.get("hash"),
                "alphabet": data.get("alphabet"),
                "start": data.get("start"),
                "count": data.get("count")
            }

            # Process the task using the controller

            thread = Thread(target=self.controller.processTask, args=(task,))
            thread.start()

            return Response(status=200)

        @self.app.route("/internal/api/worker/hash/crack/progress", methods=["GET"])
        def handle_progress():
            # Get progress from the controller and send it as a JSON response
            progress = self.controller.getProgress()
            return jsonify(progress)

    # Start the Flask server on the given port and log when started
    def start(self, port):
        print("Worker started")
        self.app.run(port=port, host='0.0.0.0')