

from bson.objectid import ObjectId, InvalidId
from datetime import datetime, date, time, timedelta
import json

import jsonschema

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
    def _work_on_str_objectid_dict_keys(_dict):

        for key, value in _dict.items():

            if key.endswith('_id') or key == '_id':
                _dict[key] = ObjectId(_dict[key])

        return _dict


    @staticmethod
    def change_all_objectids_to_str(obj):
        # encode rest response
        """
        Converts a python data object to another python object, while encoding
        all underlying ObjectIds to string
        """
        obj_json = json.dumps(obj, cls=JsonUtils.ObjectIdEncoder)
        obj_new = json.loads(obj_json)
        return obj_new


    @staticmethod
    def change_all_str_objectids_to_objectids(obj):

        obj_json = json.dumps(obj)
        obj_new = json.loads(
            obj_json, object_hook=JsonUtils._work_on_str_objectid_dict_keys
        )
        return obj_new

    @staticmethod
    def change_all_date_time_to_include_leading_zeros(obj):

        for key, value in obj.items():

            if key.endswith('_date'):
                temp = DateUtils.to_datetime_format(value, DateUtils.DATE)
                obj[key] = temp.isoformat()
            elif key.endswith('_time'):
                temp = DateUtils.to_datetime_format(value, DateUtils.TIME)
                obj[key] = temp.isoformat()
            elif key.endswith('_datetime'):
                temp = DateUtils.to_datetime_format(value, DateUtils.DATETIME)
                obj[key] = temp.isoformat()

        return obj

    @staticmethod
    def validate_json(data, schema):
        """
        Validates data against the schema"
        data - json data as a python data structure
        schema - json schema as a python dict

        throws an exception if validation fails, if not, returns None
        Returns a python dict representing the error is validation fails, else
        returns nothing
        """
        jsonschema.validate(data, schema)


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
    def is_saturday(date_str):

        _date = DateUtils.to_datetime_format(date_str, DateUtils.DATE)
        return _date.isoweekday() == 6

    @staticmethod
    def is_sunday(date_str):
        _date = DateUtils.to_datetime_format(date_str, DateUtils.DATE)
        return _date.isoweekday() == 7

    @staticmethod
    def is_weekday(date_str):
        _date = DateUtils.to_datetime_format(date_str, DateUtils.DATE)

        return _date.isoweekday() in range(1, 6)

    @staticmethod
    def to_datetime_format(str, type_of_datetime):
        """
        returns a datetime object, use date() or time() to convert it to a date
        or time object respectively or just use it as it is if datetime is what
        you need
        """
        _datetime = datetime.strptime(str, DateUtils.FORMATS[type_of_datetime])

        if type_of_datetime == DateUtils.DATE:
            return _datetime.date()
        elif type_of_datetime == DateUtils.TIME:
            return _datetime.time()

        return _datetime


    @staticmethod
    def get_dates_in_range(start_date_str,
                           end_date_str,
                           include_saturday=False,
                           include_sunday=False):
        """
        Returns a list of date objects between start and end dates(inclusive of
        both start and end dates)
        """
        date_format = DateUtils.FORMATS[DateUtils.DATE]

        _d = datetime.strptime(start_date_str, date_format)
        current_date = date(year=_d.year, month=_d.month, day=_d.day)

        _d = datetime.strptime(end_date_str, date_format)
        end_date = date(year=_d.year, month=_d.month, day=_d.day)

        dates = []
        while (end_date - current_date).total_seconds() >= 0:
            # print "current date-------", current_date
            _date_str = current_date.isoformat()
            if (
                (DateUtils.is_weekday(_date_str)) or
                (DateUtils.is_saturday(_date_str) and include_saturday) or
                (DateUtils.is_sunday(_date_str) and include_sunday)

                        # (current_date.isoweekday() in range(1, 6)) or
                        # (current_date.isoweekday() == 6 and include_saturday) or
                        # (current_date.isoweekday() == 7 and include_sunday)
            ):

                dates.append(current_date)

            current_date = current_date + timedelta(days=1)

        return dates