
from scheduling_backend.database_manager import (
    DatabaseManager,
    Collection,
    JobOperations
)

from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employeeshift
from scheduling_backend.models import EmployeeShift

class AddEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(AddEmployeeShiftHandler, self).__init__(None)

    @marshaling_handler
    def get(self, employee_id, jobshift_id):

        JobOperations.add_employee_to_jobshift(employee_id, jobshift_id)

        jobshift_dict = \
            DatabaseManager.find_document_by_id(Collection.JOBSHIFTS,
                                                jobshift_id,
                                                True)
        return jobshift_dict

class RemoveEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(RemoveEmployeeShiftHandler, self).__init__(None)

    @marshaling_handler
    def get(self, employee_id, jobshift_id):

        JobOperations.remove_employee_from_jobshift(employee_id, jobshift_id)

        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )

        return jobshift_dict

class MoveEmployeeAcrossJobshifts(BaseHandler):

    def __init__(self):
        super(MoveEmployeeAcrossJobshifts, self).__init__(None)



    def get(self, employee_id, from_jobshift_id, to_jobshift_id):

        JobOperations.move_employee_amongst_jobshifts(employee_id,
                                                      from_jobshift_id,
                                                      to_jobshift_id)

        # todo figure out what to return
        return '', 204

class ModifyEmployeeShiftHandler(BaseHandler):

    def __init__(self):
        super(ModifyEmployeeShiftHandler, self).__init__(schema_employeeshift)

    def preprocess_PATCH(self):
        employee_id = self.data.get(EmployeeShift.Fields.EMPLOYEE_ID, None)
        if employee_id:
            raise UserException("employee id cannot be present as"
                                " part of patch data")

    @marshaling_handler
    def patch(self, jobshift_id, employee_id):

        jobshift = JobOperations.find_jobshift_by_id_and_employee_id(
            jobshift_id, employee_id
        )

        if not jobshift:
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
