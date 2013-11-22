

from bson.objectid import ObjectId, InvalidId

from flask.ext.restful import Resource

from flask.ext.restful.reqparse import RequestParser

from flask import request
from scheduling_backend.models import tag_id



from scheduling_backend.utils import (
    JsonUtils, DateUtils, ObjectIdUtils
)

from scheduling_backend.handlers import MessageDict
# from scheduling_backend.json_schemas import schema_client


class BaseHandler(Resource):

    POST = "POST"
    PUT = "PUT"
    GET = "GET"
    PATCH = "PATCH"


    def __init__(self, schema):

        super(BaseHandler, self).__init__()

        self.data = None
        self.error = None
        self.schema = schema
        self.req_parser = RequestParser()

        if request.method in [BaseHandler.POST, BaseHandler.PATCH]:

            self.data = request.get_json(force=False, silent=True)

            # If data is not in json, mark it as an error
            if not self.data:
                self.error = MessageDict.request_not_in_json
            else:
                self.error = JsonUtils.validate_json(self.data, self.schema)

            # We check if _id field is present inside post/put/patch. If it is
            # we mark it as an error, because id field is autogenerated and
            # cannot be modified
            self.req_parser.add_argument(tag_id,
                                         type=str,
                                         required=False,
                                         location='json',
                                         help="_id field cannot be modified")
            self.args = self.req_parser.parse_args()
            if self.args._id:
                self.error = {"error": "_id field is autogenerated "
                                       "and cannot be present in request data"}

        if self.error:
            return

        if self.data:
            # self.data would be not one only for post or patch
            self.preprocess_data(self.data)



    def preprocess_data(self, data):
        msg = "Subclasses of Basehandler should implement preprocess_data"
        raise NotImplementedError(msg)

    @staticmethod
    def none_present_in_list(l):
        if any([True for x in l if x is None]):
            return True
        else:
            return False

    # @staticmethod
    # def is_key_present(_dict, key):
    #     value = _dict.get(key, None)
    #     if value is None:
    #         return False
    #     else:
    #         return True


    # @staticmethod
    # def is_value_not_empty(_dict, key):
    #     value = _dict.get(key, '')
    #     if value == '':
    #         return False
    #     else:
    #         return True

    def validate_field_existence(self, field_name, required):
        "Use this for validation of boolean and int fields"
        if self.error:
            return

        field_value = self.data.get(field_name, None)
        if field_value is None and required:
            self.error = {"error": "%s cannot be missing" % field_name}


    def validate_str_field(self, field_name, required):

        if self.error:
            return

        field_value = self.data.get(field_name, None)

        if field_value is None:
            self.validate_field_existence(field_name, required)

        else:
            field_value = field_value.strip()
            if field_value == '':
                self.error = {"error": "%s cannot be empty" % field_name}


    def validate_str_as_object_id_field(self, field_name, required):
        if self.error:
            return

        field_value = self.data.get(field_name, None)

        if field_value is None:
            self.validate_field_existence(field_name, required)

        else:
            if not ObjectIdUtils.valid_oid(field_value):
                self.error = {
                    "error": "%s is not a valid ObjectId string" % field_name
                }


    def validate_date_time_field(self, field_name, datetime_type, required):
        if self.error:
            return

        field_value = self.data.get(field_name, None)
        if field_value is None:
            self.validate_field_existence(field_name, required)
        else:

            field_value = self.data.get(field_name, '')

            self.error = DateUtils.validate(field_value, datetime_type)
            return self.error




    def put(self):
        return {
            "error":
                "use patch instead, and only send fields which have changed"
        }