
from scheduling_backend.database_manager import (
    DatabaseManager,
    Collection,
    JobOperations
)

from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler


class AddEquipmentShiftHandler(BaseHandler):

    def __init__(self):
        super(AddEquipmentShiftHandler, self).__init__(None)

    @marshaling_handler
    def get(self, equipment_id, jobshift_id):

        JobOperations.add_equipment_to_jobshift(
            equipment_id, jobshift_id
        )

        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        return jobshift_dict


class RemoveEquipmentShiftHandler(BaseHandler):

    def __init__(self):
        super(RemoveEquipmentShiftHandler, self).__init__(None)


    @marshaling_handler
    def get(self, equipment_id, jobshift_id):

        JobOperations.remove_equipment_from_jobshift(
            equipment_id, jobshift_id
        )
        jobshift_dict = DatabaseManager.find_document_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        return jobshift_dict


class MoveEquipmentAcrossJobshifts(BaseHandler):

    def __init__(self):
        super(MoveEquipmentAcrossJobshifts, self).__init__(None)

    def get(self, equipment_id, from_jobshift_id, to_jobshift_id):

        JobOperations.move_equipment_amongst_jobshifts(
            equipment_id, from_jobshift_id, to_jobshift_id
        )

        # todo figure out what to return
        return '', 204