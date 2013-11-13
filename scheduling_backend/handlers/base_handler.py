
from flask.ext.restful import Resource
from flask import request


from scheduling_backend.utils import (
    JsonUtils
)

from scheduling_backend.handlers import MessageDict
# from scheduling_backend.json_schemas import schema_client


class BaseHandler(Resource):

    def __init__(self, schema):

        print "Received schema", schema

        super(BaseHandler, self).__init__()

        self.data = None
        self.error = None
        self.schema = schema

        if request.method in ["PUT", "POST", "PATCH"]:

            self.data = request.get_json(force=False, silent=True)

            # If data is not in json, mark it as an error
            if not self.data:
                self.error = MessageDict.request_not_in_json
            else:
                self.error = JsonUtils.validate_json(self.data, self.schema)

            if self.error:
                return


    def put(self):
        return {"error": "use patch instead, and only send fields which have changed"}