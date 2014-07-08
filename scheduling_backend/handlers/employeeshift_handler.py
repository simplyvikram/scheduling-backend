
from scheduling_backend.database_manager import (
    DatabaseManager,
    Collection,
    JobOperations
)

from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import no_data_handler, marshaling_handler, \
    Params
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employeeshift
from scheduling_backend.models import EmployeeShift, Employee

class AddEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(AddEmployeeShiftHandler, self).__init__(None)

        AddEmployeeShiftHandler.validate_shift_role = _validate_shift_role

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.SHIFT_ROLE,
                                     type=str,
                                     location='args',
                                     required=False,
                                     default=None)

        self.args = self.req_parser.parse_args()

    @marshaling_handler
    def get(self, employee_id, jobshift_id):

        shift_role = self.args.get(Params.SHIFT_ROLE, None)
        self.validate_shift_role(shift_role)

        JobOperations.add_employee_to_jobshift(
            employee_id, jobshift_id, shift_role
        )

        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        return jobshift_dict


class RemoveEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(RemoveEmployeeShiftHandler, self).__init__(None)


    @marshaling_handler
    def get(self, employee_id, jobshift_id):

        JobOperations.remove_employee_from_jobshift(
            employee_id, jobshift_id
        )
        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        return jobshift_dict

class MoveEmployeeAcrossJobshifts(BaseHandler):

    def __init__(self):
        super(MoveEmployeeAcrossJobshifts, self).__init__(None)

        MoveEmployeeAcrossJobshifts.validate_shift_role = _validate_shift_role

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.SHIFT_ROLE,
                                     type=str,
                                     location='args',
                                     required=False,
                                     default=None)

        self.args = self.req_parser.parse_args()


    @no_data_handler
    def get(self, employee_id, from_jobshift_id, to_jobshift_id):

        shift_role = self.args.get(Params.SHIFT_ROLE, None)
        self.validate_shift_role(shift_role)

        JobOperations.move_employee_amongst_jobshifts(
            employee_id, from_jobshift_id, to_jobshift_id, shift_role
        )

        # todo figure out what to return
        return '', 204

class ModifyEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(ModifyEmployeeShiftHandler, self).__init__(schema_employeeshift)
        ModifyEmployeeShiftHandler.validate_shift_role = _validate_shift_role

    def preprocess_PATCH(self):
        employee_id = self.data.get(EmployeeShift.Fields.EMPLOYEE_ID, None)
        if employee_id:
            raise UserException("employee id cannot be present as"
                                " part of patch data")

    @marshaling_handler
    def patch(self, jobshift_id, employee_id):

        shift_role = self.data.get(EmployeeShift.Fields.SHIFT_ROLE, None)
        self.validate_shift_role(shift_role)

        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id
        )

        if not jobshift.contains_employee(employee_id):
            msg = "The employee _id:%s is not scheduled for jobshift " \
                  "_id: %s. Please add him to the jobshift first" % \
                  (employee_id, jobshift_id)

            raise UserException(msg)

        JobOperations.modify_employee_shift(
            employee_id, jobshift_id, self.data
        )

        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        return jobshift_dict


def _validate_shift_role(self, shift_role):

    if (shift_role is not None) and\
            (shift_role not in Employee.allowed_roles()):

        msg = "{0} does not contain a valid value. Only {1} are allowed".format(
            EmployeeShift.Fields.SHIFT_ROLE, str(Employee.allowed_roles())
        )
        raise UserException(msg)


