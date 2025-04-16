# This code is a translation from JavaScript using Express framework to Python using Flask framework.
import uuid

from flask import Flask, request, jsonify

from manager import Manager

class ManagerService:
    def __init__(self, manager):
        self.app = Flask(__name__)
        self.manager = manager

        @self.app.route("/api/hash/crack", methods=['POST'])
        def crack_hash():
            if not request.json:
                return '', 400

            request_data = {
                'id': uuid.uuid4(),
                'hash': request.json['hash'],
                'maxLength': request.json['maxLength']
            }

            request_id = self.manager.handle_request(request_data)
            if request_id:
                return jsonify({'requestId': request_id})
            else:
                return '', 429

        @self.app.route("/api/hash/status", methods=['GET'])
        def hash_status():
            request_id = request.args.get('requestId')

            if not self.manager.has_request(request_id):
                return '', 400

            status = self.manager.get_request_status(request_id)
            return jsonify(status)

        @self.app.route("/internal/api/manager/hash/crack/request", methods=['PATCH'])
        def update_hash_request():
            if not request.json:
                return '', 400

            request_id = request.json['requestId']
            if not self.manager.has_request(request_id):
                return '', 400

            data = request.json['data']
            self.manager.update_request_data(request_id, data)

            return '', 200

    def start(self, port):
        self.app.run(port=port, host='0.0.0.0')
        print("Manager started")