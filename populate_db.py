
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json


from scheduling_backend.models import Client, Job, BaseModel, Employee


client = MongoClient('localhost', 27017)
db = client.test_db
base_url = 'http://127.0.0.1:5000'


def insert_clients():

    for x in range(1, 5):
        name = "client " + str(x)
        active = True
        client = Client(name, active)
        db.clients.insert(Client.encode(client))


def insert_employee():
    name = "employee_ " + str(1)

    active = True
    default_role = Employee.allowed_roles()[0]
    employee = Employee(name, default_role, active)

    db.employees.insert(Employee.encode(employee))


def list_all():

    c = db.clients.find()
    clients = list(c)

    for client in clients:
        print "\nClient -----", client

    print '\n\n'

    c = db.employees.find()
    employees = list(c)
    for employee in employees:
        print "\nEmployee ----", employee


def create_jobs():
    c = db.clients.find()

    clients = list(c)

    job_url = base_url + '/jobs'

    for client in clients:
        client = Client(**client)

        payload = dict()
        payload[Job.Fields.CLIENT_ID] = str(client._id)
        payload[Job.Fields.NAME] = client.name + '_job'
        payload[Job.Fields.LOCATION] = 'Miami'
        payload[Job.Fields.START_DATE] = '2014-03-12'
        payload[Job.Fields.END_DATE] = '2014-03-22'
        payload[Job.Fields.SCHEDULED_START_TIME] = '08:00:00'
        payload[Job.Fields.SCHEDULED_END_TIME] = '17:00:00'

        headers = {'content-type': 'application/json'}

        response = requests.post(job_url, data=json.dumps(payload), headers=headers)

        response.json()
        if response.status_code == 200:
            print 'Job created for client ', str(client._id)


if __name__ == '__main__':

    # list_all_clients()
    # insert_clients()

    # create_jobs()

    insert_employee()
    list_all()




