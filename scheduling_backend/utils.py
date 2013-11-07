
import json
from bson.objectid import ObjectId

import jsonschema
from jsonschema import ValidationError, SchemaError

from flask import current_app as current_app


class VEncoder(json.JSONEncoder):
    """
    Encodes python data structure to json while converting ObjectIds
    to string format
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def encode_rest_response(obj_py):
    """
    Converts a python data object to another python object, while encoding
    all underlying ObjectIds to string
    """
    obj_json = json.dumps(obj_py, cls=VEncoder)
    obj_py_new = json.loads(obj_json)
    return obj_py_new


def validate_json(data, schema):
    """
    Validates data againgst the schema"
    data - json data as a python datastructure
    schema - json schema as a python dict
    """

    try:
        jsonschema.validate(data, schema)
    except (ValidationError, SchemaError) as e:
        current_app.logger.error(repr(e))
        return False, {'error': repr(e)}

    return True, None


# def decoder(dct):
#     for key, value in dct.items():
#         if key.endswith('_id'):
#             dct[key] = ObjectId(dct[key])
#         return dct
