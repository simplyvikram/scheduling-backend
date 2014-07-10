
import flask

from bson.objectid import ObjectId
from scheduling_backend.database_manager import DatabaseManager, Collection
from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import marshaling_handler, delete_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_equipment
from scheduling_backend.models import BaseModel, Equipment

class EquipmentHandler(BaseHandler):

    def __init__(self):
        super(EquipmentHandler, self).__init__(schema_equipment)

    def preprocess_PATCH(self):

        # caution -
        # Super hackish way to extract the object id as
        # reqparse wasn't working as expected
        path = flask.request.path
        equipment_id = path[-24:]

        type = self.data.get(Equipment.Fields.TYPE, None)
        if type is not None:
            self._validate_equipment_type(type)

        name = self.data.get(Equipment.Fields.NAME, None)
        self.validate_name(
            name,
            Collection.EQUIPMENT,
            Equipment.Fields.NAME,
            ObjectId(equipment_id)
        )


    def preprocess_POST(self):
        name = self.data.get(Equipment.Fields.NAME, None)
        type = self.data.get(Equipment.Fields.TYPE, None)

        self._validate_equipment_type(type)
        self.validate_name(
            name,
            Collection.EQUIPMENT,
            Equipment.Fields.NAME
        )


    @marshaling_handler
    def get(self, obj_id=None):

        if obj_id:
            equipment_dict = DatabaseManager.find_document_by_id(
                Collection.EQUIPMENT, obj_id, True
            )
            return equipment_dict
        else:
            equipment_list = DatabaseManager.find(
                Collection.EQUIPMENT, {}, True
            )
            return equipment_list


    @marshaling_handler
    def post(self):
        """
        We always try to create an Equipment object from the data posted, to
        make sure we have all the required data, if anything is absent, an
        exception will be raised
        """
        print "self.data------", self.data
        equipment = Equipment(**self.data)
        _dict = Equipment.encode(equipment)

        print "-----", _dict

        _id = DatabaseManager.insert(Collection.EQUIPMENT, _dict)

        equipment_dict = DatabaseManager.find_document_by_id(
            Collection.EQUIPMENT, _id, True
        )
        return equipment_dict


    @marshaling_handler
    def patch(self, obj_id):

        query = {BaseModel.Fields._ID: obj_id}
        update = {'$set': self.data}

        _ = DatabaseManager.update(
            Collection.EQUIPMENT, query, update, multi=False, upsert=False
        )
        equipment_dict = DatabaseManager.find_document_by_id(
            Collection.EQUIPMENT, obj_id, True
        )

        return equipment_dict


    @delete_handler
    def delete(self, obj_id):

        result = DatabaseManager.remove(
            Collection.EQUIPMENT,
            {BaseModel.Fields._ID: obj_id},
            multiple=False
        )

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404


    def _validate_equipment_type(self, type):
        """
        We check that the equipment type if present, is a valid one
        """
        if type == '':
            raise UserException('Equipment type cannot be empty')

        elif type not in Equipment.allowed_types():
            msg ="Allowed types for equipment type are {0}".format(
                str(Equipment.allowed_types())
            )
            raise UserException(msg)