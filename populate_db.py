
from pymongo import MongoClient
from bson.objectid import ObjectId
from scheduling_backend.models import Client
client = MongoClient('localhost', 27017)
db = client.test_db


def insert_clients():

    for x in range(1, 5):
        name = "client " + str(x)
        active = True

        client = Client(name, active)

        db.clients.insert(Client.encode(client))

def list_all_clients():

    c = db.clients.find()

    clients = list(c)

    for client in clients:
        print "\n\nClient -----", client

if __name__ == '__main__':
    insert_clients()

    list_all_clients()
    insert_clients()
