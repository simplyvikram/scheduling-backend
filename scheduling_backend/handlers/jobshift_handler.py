
from flask import current_app as current_app

from scheduling_backend.models import JobShift, EmployeeShift
from scheduling_backend.handlers import common_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_job_shift, \
    schema_employee_shift


class JobShiftHandler(BaseHandler):

    def __init__(self):
        print "hello2"
        super(JobShiftHandler, self).__init__(schema_job_shift)


    def preprocess_data(self, data):
        # todo fill later
        pass

    @common_handler
    def get(self, job_shift_id=None):
        return {"method": "GET job shift"}

    @common_handler
    def post(self):
        return {"error": "Job shifts cannot be created using apis"}

    @common_handler
    def delete(self):
        """
        The user may want to delete job shifts in case of holidays etc
        """
        return {"Implement me!!!!": True}


    @common_handler
    def add_employeeshift(self):
        return {"msg": "inside addemployee shift"}