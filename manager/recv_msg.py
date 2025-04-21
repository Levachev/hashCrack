from status import Status

class Request:
    def __init__(self, id, hash, max_length):
        self.status = Status["InProgress"]
        self.data = []
        self.timer_id = 0
        self.id = id
        self.hash = hash
        self.max_length = max_length

    def get_status_with_progress(self, progress):
        status = self.get_status()
        print("progress  ", progress)
        status["progress"] = progress
        return status

    def get_status(self):
        data = self.data if self.data else None
        return {
            'status': self.status,
            'data': data,
        }

    def set_error_status(self, repo):
        if self.status == Status["InProgress"]:
            self.status = Status["Err"]
        repo.update(rid=self.id, request=self)

    def in_progress(self):
        return self.status in (Status["InProgress"], Status["Partial"])

    def add_data(self, data, repo):
        self.data.extend(data)
        self.status = Status["Partial"]
        repo.update(rid=self.id, request=self)

    def complete(self, repo):
        self.status = Status["Ready"]
        repo.update(rid=self.id, request=self)