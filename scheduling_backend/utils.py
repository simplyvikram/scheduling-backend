

from bson.objectid import ObjectId, InvalidId
from datetime import date, datetime, time, timedelta
import json

import jsonschema
from jsonschema import ValidationError, SchemaError


class JsonUtils(object):

    class ObjectIdEncoder(json.JSONEncoder):
        """
        Encodes python data structure to json while converting ObjectIds
        to string format
        """
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            else:
                return json.JSONEncoder.default(self, obj)


    @staticmethod
    def _work_on_dict_keys(_dict):
        for key, value in _dict.items():

            if key.endswith('_id') or key == '_id':
                _dict[key] = ObjectId(_dict[key])

        return _dict


    @staticmethod
    def change_str_ids_to_object_id(obj):

        obj_json = json.dumps(obj)
        obj_new = json.loads(obj_json, object_hook=JsonUtils._work_on_dict_keys)
        return obj_new


    @staticmethod
    def change_obj_ids_to_str_ids(obj):
        # encode rest response
        """
        Converts a python data object to another python object, while encoding
        all underlying ObjectIds to string
        """
        obj_json = json.dumps(obj, cls=JsonUtils.ObjectIdEncoder)
        obj_new = json.loads(obj_json)
        return obj_new

    @staticmethod
    def validate_json(data, schema):
        """
        Validates data against the schema"
        data - json data as a python data structure
        schema - json schema as a python dict

        Returns a python dict representing the error is validation fails, else
        returns nothing
        """

        try:
            jsonschema.validate(data, schema)
        except (ValidationError, SchemaError) as e:
            return {'error': repr(e)}


class DateUtils(object):
    DATE = "DATE"
    DATETIME = "DATETIME"
    TIME = "TIME"

    _date_format = "%Y-%m-%d"
    _time_format = "%H:%M:%S"

    FORMATS = {
        DATE: _date_format,
        TIME: _time_format,
        DATETIME: _date_format + "T" + _time_format
    }


    @staticmethod
    def validate(datetime_str, type_of_datetime):
        """
        Returns an error message in python dict in case date/time/datetime is
        not a valid one in iso8601 format, else does nothing
        """
        if not datetime_str:
            return {"error": type_of_datetime + " cannot be empty/None!"}

        if type_of_datetime not in [DateUtils.DATE,
                                    DateUtils.TIME,
                                    DateUtils.DATETIME]:
            return {"error": "wrong datetime format"}

        try:
            print "DATEUTILS validating date:%s  format:%s" % \
                  (datetime_str, DateUtils.FORMATS[type_of_datetime])

            _datetime = datetime.strptime(datetime_str,
                                          DateUtils.FORMATS[type_of_datetime])
        except Exception as e:

            error = {"error": str(e),
                     "message": "Date/Time/Datetime is not in the right format"}
            print "Exception - ", error
            return error


class ObjectIdUtils(object):

    @staticmethod
    def valid_oid(str_id):
        try:
            ObjectId(str_id)
            return True
        except InvalidId:
            return False