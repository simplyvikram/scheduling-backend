
tag_id = "_id"


class Client(object):
    tag_name = "name"
    tag_active = "active"

    def __init__(self, name, active):
        self._id = None
        self.name = name
        self.active = active

    @staticmethod
    def encode(obj):
        d = {
            Client.tag_name: obj.name,
            Client.tag_active: obj.active
        }
        if obj._id is not None:
            d[tag_id] = obj._id

        return d


class Job(object):
    tag_client_id = "client_id"
    tag_name = "name"
    tag_start_date = "start_date"
    tag_end_date = "end_date"
    tag_location = "location"

    def __init__(self, client_id, name, start_date, end_date, location):
        self.client_id = client_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location

    @staticmethod
    def encode(obj):
        d = {
            Job.tag_client_id: obj.client_id,
            Job.tag_name: obj.name,
            Job.tag_start_date: obj.start_date,
            Job.tag_end_date: obj.end_date,
            Job.tag_location: obj.location
        }
        if obj.id is not None:
            d[tag_id] = obj._id

        return d


class Employee(object):

    @classmethod
    def roles(cls):
        return ['plumber', 'worker', 'carpenter', 'fitter']

    tag_name = "name"
    tag_current_role = "current_role"
    tag_active = "active"

    def __init__(self, name, current_role, active):
        self._id = None
        self.name = name
        self.current_role = current_role
        self.active = active

    @staticmethod
    def encode(obj):
        d = {
            Employee.tag_name: obj.name,
            Employee.tag_current_role: obj.current_role,
            Employee.tag_active: obj.active
        }
        if obj._id is not None:
            d[tag_id] = obj._id

        return d