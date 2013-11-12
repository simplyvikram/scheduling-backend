
from flask.ext.restful import Resource
from flask import request
from flask import current_app as current_app

from scheduling_backend.utils_new import (
    JsonUtils
)
from scheduling_backend.handlers import MessageDict, object_id_handler
from scheduling_backend.json_schemas import schema_client


class ClientHandler(Resource):

    def __init__(self):
        super(ClientHandler, self).__init__()
        self.data = None
        self.error = None

        if request.method in ["PUT", "POST", "PATCH"]:

            self.data = request.get_json(force=False, silent=True)

            # If data is not in json, mark it as an error
            if not self.data:
                self.error = MessageDict.request_not_in_json
            else:
                self.error = JsonUtils.validate_json(self.data, schema_client)

            if self.error:
                return

    @object_id_handler
    def get(self, obj_id=None):

        if obj_id:
            client = current_app.db.clients.find_one({"_id": obj_id})
            if client is None:
                return {}

            return client

        else:
            clients_cursor = current_app.db.clients.find()
            clients_list = list(clients_cursor)

            return clients_list


    @object_id_handler
    def post(self):

        if self.error:
            return self.error

        obj_id = current_app.db.clients.insert(self.data)
        # todo can the data have an array of clients to be inserted????
        client = current_app.db.clients.find_one({"_id": obj_id})

        return client


    @object_id_handler
    def patch(self, obj_id):

        if self.error:
            return self.error

        current_app.db.clients.update({"_id": obj_id}, {'$set': self.data})

        client = current_app.db.clients.find_one({"_id": obj_id})
        return client


    def delete(self, obj_id):

        # todo can the data have an array of clients to be deleted????
        result = current_app.db.clients.remove({"_id": obj_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404