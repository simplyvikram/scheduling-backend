


from flask.ext.restful import Resource
from flask import request


from scheduling_backend.utils import (
    JsonUtils
)

from scheduling_backend.handlers import MessageDict
# from scheduling_backend.json_schemas import schema_client


class BaseHandler(Resource):


    def __init__(self, schema):

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
                print "\n\nVALIDATING", self.data, "\n\nAGAINST", schema
                self.error = JsonUtils.validate_json(self.data, self.schema)

        if self.error:
            return

        if self.data:
            # self.data would be not one only for post or patch
            self.preprocess_data(self.data)


    def preprocess_data(self, data):
        msg = "Subclasses of Basehandler should implement preprocess_data"
        raise NotImplementedError(msg)


    def put(self):
        return {
            "error":
                "use patch instead, and only send fields which have changed"
        }