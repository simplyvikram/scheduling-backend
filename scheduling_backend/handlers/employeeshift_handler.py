from flask import current_app as current_app

from scheduling_backend.models import JobShift, EmployeeShift
from scheduling_backend.handlers import common_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_job_shift, \
    schema_employee_shift


class EmployeeShiftHandler(BaseHandler):
    pass