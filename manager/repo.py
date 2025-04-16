from pymongo import MongoClient

class Repo:
    def __init__(self):
        self.client = MongoClient('mongodb://mongodb1:27017,mongodb2:27018,mongodb3:27019/?replicaSet=rs0&w=majority')
        self.db = self.client["db"]
        self.collection = self.db["my_collection"]

    def count(self):
        return self.collection.count_documents({})

    def save_request(self, request):
        try:
            if self.collection.find_one({"_id": request.id}) is not None:
                return
            print("before")
            data = {
                '_id': request.id,
                'hash': request.hash,
                'maxLength': request.max_length,
                'status': request.status,
                'data': request.data
            }

            # Inserting the student data into the 'students' collection and obtaining the inserted ID
            rid = self.collection.insert_one(data).inserted_id

            # Printing a message indicating the successful insertion of data with the obtained ID
            print(f"Data inserted with ID: {rid}")
        except Exception as e:
            # Handling exceptions and printing an error message if data insertion fails
            print(f"Error: {e}")

    def fetch_all(self):
        # Querying the 'students' collection to find all data
        data = self.collection.find()
        return data

    def update(self, rid, request):
        # Creating a dictionary with updated student details
        data = {
            'hash': request.hash,
            'maxLength': request.max_length,
            'status': request.status,
            'data': request.data
        }
        # Updating the student data in the 'students' collection
        self.collection.update_one({'_id': rid}, {"$set": data})

    def delete(self, rid):
        # Deleting a student's data from the 'students' collection based on student ID
        self.collection.delete_one({'_id': rid})

# repo = Repo()
# print(repo.count())