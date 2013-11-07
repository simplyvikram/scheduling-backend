from datetime import date, datetime, time, timedelta
from random import randint
from scheduling_backend.models import Client, Job
import json
import urllib2

today_date = date.today()


headers = {'Content-type': 'application/json'}


def generate_client_dict(name, active):

    client = Client(name, active)
    return Client.encode(client)


def generate_job(client_id, client_name, location):

    start_date = date.today() + timedelta(days=randint(4, 10))
    end_date = date.today() + timedelta(days=randint(15, 25))

    # def __init__(self, client_id, start_date, end_date, location):

    job = Job(client_id=client_id, start_date=start_date, end_date=end_date,
              location=location)

    return Job.encode(job)


def client_post():
    req = urllib2.Request('http://127.0.0.1:5000/clients')
    req.headers = headers

    client_dict = generate_client_dict("vikram", True)
    resp = urllib2.urlopen(req, json.dumps(client_dict))

    resp_data = resp.read()

    print "Response json str - ", resp_data
    print "Response python dict ", json.loads(resp_data)
    print "Response content-type -", resp.info().getheader('Content-Type')

if __name__ == '__main__':
    client_post()



