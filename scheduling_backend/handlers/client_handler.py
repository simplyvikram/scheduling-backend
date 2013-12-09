
import flask.ext.restful.types

from flask import current_app as current_app

from scheduling_backend.handlers import marshaling_handler, Params
from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_client
from scheduling_backend.models import BaseModel, Client


class ClientHandler(BaseHandler):

    def __init__(self):
        super(ClientHandler, self).__init__(schema_client)

    def preprocess(self):
        self.req_parser.add_argument(Params.ACTIVE,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     default=None,
                                     required=False)

        self.args = self.req_parser.parse_args()

        super(ClientHandler, self).preprocess()

    def preprocess_PATCH(self):
        name = self.data.get(Client.Fields.NAME, None)
        self._validate_client_name(name)


    def preprocess_POST(self):
        self.preprocess_PATCH()


    def _validate_client_name(self, client_name):
        """
        We check if the client name, if present is a valid one
        """
        if client_name == '':
            raise UserException("Client name cannot be empty")

        matching_client_count = current_app.db.clients.find(
            {Client.Fields.NAME: client_name}
        ).count()

        if matching_client_count > 0:
            raise UserException("Duplicate user name, choose another name.")


    @marshaling_handler
    def get(self, obj_id=None):

        if obj_id:
            client = current_app.db.clients.find_one(
                {BaseModel.Fields._ID: obj_id}
            )
            if client is None:
                return {}

            return client

        else:
            query_dict = {}
            active = self.args.get(Params.ACTIVE, None)

            # active is an optional param, it may or may not be present. Hence
            # we explicitly check it with True or False.
            # if absent it will be None

            if active is True:
                query_dict[Client.Fields.ACTIVE] = True
            elif active is False:
                query_dict[Client.Fields.ACTIVE] = False

            clients_cursor = current_app.db.clients.find(query_dict)
            clients_list = list(clients_cursor)

            return clients_list


    @marshaling_handler
    def post(self):
        # We create a Client to make sure we have all the data we need to
        # create a client, if not an exception is raised
        client = Client(**self.data)
        _dict = Client.encode(client)

        obj_id = current_app.db.clients.insert(_dict)
        # todo can the data have an array of clients to be inserted????
        client_dict = current_app.db.clients.find_one(
            {BaseModel.Fields._ID: obj_id}
        )

        return client_dict


    @marshaling_handler
    def patch(self, obj_id):

        _dict = self.data

        current_app.db.clients.update(
            {BaseModel.Fields._ID: obj_id}, {'$set': _dict}
        )
        client_dict = current_app.db.clients.find_one(
            {BaseModel.Fields._ID: obj_id}
        )
        return client_dict


    # @marshaling_handler
    def delete(self, obj_id):

        # todo can the data have an array of clients to be deleted????
        result = current_app.db.clients.remove({BaseModel.Fields._ID: obj_id})

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404