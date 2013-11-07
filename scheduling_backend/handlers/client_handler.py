
from flask.ext.restful import Resource
from flask import request
from flask import current_app as current_app


from scheduling_backend.utils import (
    encode_rest_response,
    validate_json
)
from scheduling_backend.handlers import MessageDict
from scheduling_backend.json_schemas import schema_client


class ClientHandler(Resource):


    def __init__(self):
        super(ClientHandler, self).__init__()

        if request.method in ["PUT", "POST", "PATCH"]:

            self.data = request.get_json(force=False, silent=True)
            self.error = None

            # If data is not in json, mark it as an error
            if not self.data:
                self.error = MessageDict.request_not_in_json
            else:
                valid, error_msg = validate_json(self.data, schema_client)
                if not valid:
                    self.error = error_msg


    def get(self, obj_id=None):

        if obj_id:

            client = current_app.db.clients.find_one({"_id": obj_id})

            client_encoded = encode_rest_response(client)
            return client_encoded

        else:
            clients_cursor = current_app.db.clients.find()
            clients_list = list(clients_cursor)

            clients_encoded = encode_rest_response(clients_list)
            return clients_encoded


    def patch(self, obj_id):

        if self.error:
            return self.error

        current_app.db.clients.update({"_id": obj_id}, {'$set': self.data})

        client = current_app.db.clients.find_one({"_id": obj_id})
        client_encoded = encode_rest_response(client)

        return client_encoded


    def post(self):

        if self.error:
            return self.error

        obj_id = current_app.db.clients.insert(self.data)
        # todo can the data have an array of clients to be inserted????
        client = current_app.db.clients.find_one({"_id": obj_id})
        client_encoded = encode_rest_response(client)

        return client_encoded


    def delete(self, obj_id):

        # todo can the data have an array of clients to be deleted????
        result = current_app.db.clients.remove({"_id": obj_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404
