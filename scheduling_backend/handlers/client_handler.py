
import flask.ext.restful.types

from bson.objectid import ObjectId

from scheduling_backend.database_manager import DatabaseManager, Collection
from scheduling_backend.handlers import (
    authentication_handler, delete_handler,
    marshaling_handler, Params
)
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_client
from scheduling_backend.models import BaseModel, Client


class ClientHandler(BaseHandler):

    def __init__(self):
        super(ClientHandler, self).__init__(schema_client)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.ACTIVE,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     default=None,
                                     required=False)

        self.args = self.req_parser.parse_args()

    def preprocess_PATCH(self):

        # caution -
        # Super hackish way to extract the object id as
        # reqparse wasn't working as expected
        path = flask.request.path
        client_id = path[-24:]

        client_name = self.data.get(Client.Fields.NAME, None)
        self.validate_name(
            client_name,
            Collection.CLIENTS,
            Client.Fields.NAME,
            ObjectId(client_id)
        )


    def preprocess_POST(self):
        client_name = self.data.get(Client.Fields.NAME, None)
        self.validate_name(
            client_name,
            Collection.CLIENTS,
            Client.Fields.NAME
        )


    @authentication_handler
    @marshaling_handler
    def get(self, obj_id=None):

        if obj_id:
            client_dict = DatabaseManager.find_document_by_id(
                Collection.CLIENTS, obj_id, True
            )
            return client_dict

        else:
            query = {}
            active = self.args.get(Params.ACTIVE, None)

            # active is an optional param, it may or may not be present. Hence
            # we explicitly check it with True or False.
            # if absent it will be None

            if active is True:
                query[Client.Fields.ACTIVE] = True
            elif active is False:
                query[Client.Fields.ACTIVE] = False

            clients_list = DatabaseManager.find(
                Collection.CLIENTS, query, True
            )

            return clients_list


    @authentication_handler
    @marshaling_handler
    def post(self):
        # We create a Client to make sure we have all the data we need to
        # create a client, if not an exception is raised
        client = Client(**self.data)
        _dict = Client.encode(client)

        _id = DatabaseManager.insert(Collection.CLIENTS, _dict)

        client_dict = DatabaseManager.find_document_by_id(
            Collection.CLIENTS, _id, True
        )

        return client_dict

    @authentication_handler
    @marshaling_handler
    def patch(self, obj_id):

        query_dict = {BaseModel.Fields._ID: obj_id}
        update_dict = {'$set': self.data}

        result = DatabaseManager.update(
            Collection.CLIENTS,
            query_dict,
            update_dict,
            multi=False, upsert=False
        )

        client_dict = DatabaseManager.find_document_by_id(
            Collection.CLIENTS, obj_id, True
        )
        return client_dict

    @authentication_handler
    @delete_handler
    def delete(self, obj_id):

        # todo can the data have an array of clients to be deleted????
        result = DatabaseManager.remove(
            Collection.CLIENTS,
            {BaseModel.Fields._ID: obj_id},
            multiple=False
        )

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404