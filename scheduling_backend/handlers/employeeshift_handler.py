
from scheduling_backend.database_manager import (
    DatabaseManager,
    Collection,
    JobOperations
)

from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employeeshift


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

    @marshaling_handler
    def patch(self, employee_id, jobshift_id):

        # todo implement later
        return {
            "class": "ModifyEmployeeShiftHandler",
            "method": "patch",
            "employee_id": employee_id,
            "jobshift_id": jobshift_id
        }