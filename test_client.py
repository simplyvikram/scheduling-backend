from datetime import date, datetime, time, timedelta
import random
from scheduling_backend.models import Client, Job
import json

import urllib2

today_date = date.today()


headers = {'Content-type': 'application/json'}


def generate_client_dict(name, active):
    client = Client(name, active)
    return Client.encode(client)


def generate_job(client_id, client_name, location):

    start_date = date.today() + timedelta(days=random.randint(4, 10))
    end_date = date.today() + timedelta(days=random.randint(15, 25))

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


def generate_a_few_dates():

    def print_date(_datetime):

        hour_choices = {"start": [7, 8, 9], "end": [3, 4, 5]}
        minute_choices = [0, 15, 30, 45]

        _date = date(_datetime.year, _datetime.month, _datetime.day)
        _start_time = time(random.choice(hour_choices["start"]),
                           random.choice(minute_choices))

        _end_time = time(random.choice(hour_choices["end"]),
                         random.choice(minute_choices))

        print _datetime.isoformat()
        print "   Datetime (ISO)   -", _datetime.isoformat()
        print "   Date(ISO)        -", _date.isoformat()
        print "   Start Time(ISO)  -", _start_time.isoformat()
        print "   Start Time(ISO)  -", _end_time.isoformat()

    now = datetime.now()

    print "\n\n PAST"
    for x in xrange(1, 4):
        _datetime = now - timedelta(days=random.randint(7, 14))
        print_date(_datetime)

    print "\n\n\n FUTURE"
    for x in xrange(1, 4):
        _datetime = now + timedelta(days=random.randint(7, 14))
        print_date(_datetime)

if __name__ == '__main__':
    generate_a_few_dates()
    # client_post()



