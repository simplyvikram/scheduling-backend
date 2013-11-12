

from flask.ext.restful import Resource


class EmployeeHandler(Resource):

    def __init__(self):
        super(EmployeeHandler, self).__init__()


    def get(self):

        return {"GET": "nothing"}

    def post(self):

        return {"POST": "nothing"}
