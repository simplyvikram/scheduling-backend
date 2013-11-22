
from flask.ext.restful import Resource
from flask import request
from flask import current_app as current_app

from scheduling_backend.utils import (
    JsonUtils
)
from scheduling_backend.handlers import common_handler
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_client
from scheduling_backend.models import Client


class ClientHandler(BaseHandler):

    def __init__(self):
        super(ClientHandler, self).__init__(schema_client)

    def preprocess_data(self, data):
        if self.error:
            return
        if request.method == BaseHandler.POST:
            self._validate_post_data()
        elif request.method == BaseHandler.PATCH:
            self._validate_patch_data()



    def _validate_patch_data(self):

        if self.error:
            return

        self.validate_str_field(Client.Fields.NAME, False)
        self.validate_field_existence(Client.Fields.ACTIVE, False)

        # Additional check for duplicate name
        name = self.data.get(Client.Fields.NAME, None)
        if name is not None:
            is_name_duplicate = self._check_client_name_in_database(name)
            if is_name_duplicate:
                self.error = {"error": "Duplicate client name. "
                                       "Choose another name"}
                return


    def _validate_post_data(self):
        if self.error:
            return

        name = self.data.get(Client.Fields.NAME, None)
        active = self.data.get(Client.Fields.ACTIVE, None)

        l = [name, active]

        is_any_field_missing = BaseHandler.none_present_in_list(l)

        if is_any_field_missing:
            self.error = {"error": "Missing required field"}
            return

        self._validate_patch_data()


    def _check_client_name_in_database(self, client_name):

        matching_client_count = \
            current_app.db.clients.find({Client.Fields.NAME: client_name}).count()

        if matching_client_count > 0:
            return True

        return False

    @common_handler
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


    @common_handler
    def post(self):

        obj_id = current_app.db.clients.insert(self.data)
        # todo can the data have an array of clients to be inserted????
        client = current_app.db.clients.find_one({"_id": obj_id})

        return client


    @common_handler
    def patch(self, obj_id):

        current_app.db.clients.update({"_id": obj_id}, {'$set': self.data})

        client = current_app.db.clients.find_one({"_id": obj_id})
        return client


    # @common_handler
    def delete(self, obj_id):

        # todo can the data have an array of clients to be deleted????
        result = current_app.db.clients.remove({"_id": obj_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404