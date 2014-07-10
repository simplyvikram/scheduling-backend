
from scheduling_backend.database_manager import (
    DatabaseManager,
    Collection,
    JobOperations
)

from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import marshaling_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_equipmentshift
from scheduling_backend.models import EquipmentShift


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


class ModifyEquipmentShiftHandler(BaseHandler):
    def __init__(self):
        super(ModifyEquipmentShiftHandler, self).__init__(schema_equipmentshift)

    def preprocess_PATCH(self):
        for key in self.data.keys():
            if key not in [EquipmentShift.Fields.NOTE]:
                raise UserException("Only the note can be modified")


    @marshaling_handler
    def patch(self, jobshift_id, equipment_id):
        jobshift = DatabaseManager.find_object_by_id(
            Collection.JOBSHIFTS, jobshift_id, True
        )
        if not jobshift.contains_equipment(equipment_id):
            msg = "The equipment _id:%s is not scheduled for jobshift " \
                  "_id: %s. Please add the equipment to the jobshift first" % \
                  (equipment_id, jobshift_id)

            raise UserException(msg)

        JobOperations.modify_equipment_shift(
            equipment_id, jobshift_id, self.data
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