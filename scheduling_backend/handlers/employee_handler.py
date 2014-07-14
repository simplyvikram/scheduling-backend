

from bson.objectid import ObjectId

import flask.ext.restful.types

from scheduling_backend.database_manager import Collection, DatabaseManager
from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import (
    authentication_handler, marshaling_handler, Params, delete_handler
)
from scheduling_backend.handlers.base_handler import BaseHandler
from scheduling_backend.json_schemas import schema_employee
from scheduling_backend.models import BaseModel, Employee


class EmployeeHandler(BaseHandler):

    def __init__(self):
        super(EmployeeHandler, self).__init__(schema_employee)

    def preprocess_GET(self):
        self.req_parser.add_argument(Params.ACTIVE,
                                     type=flask.ext.restful.types.boolean,
                                     location='args',
                                     default=None,
                                     required=False)

        self.req_parser.add_argument(Params.DEFAULT_ROLE,
                                     type=str,
                                     location='args',
                                     default=None,
                                     required=False)

        self.args = self.req_parser.parse_args()


    def preprocess_PATCH(self):

        # caution -
        # Super hackish way to extract the object id as
        # reqparse wasn't working as expected
        path = flask.request.path
        employee_id = path[-24:]

        default_role = self.data.get(Employee.Fields.DEFAULT_ROLE, None)
        if default_role is not None:
            self._validate_default_role(default_role)

        name = self.data.get(Employee.Fields.NAME, None)
        self.validate_name(
            name,
            Collection.EMPLOYEES,
            Employee.Fields.NAME,
            ObjectId(employee_id)
        )


    def preprocess_POST(self):
        name = self.data.get(Employee.Fields.NAME, None)
        default_role = self.data.get(Employee.Fields.DEFAULT_ROLE, None)

        self._validate_default_role(default_role)
        self.validate_name(
            name,
            Collection.EMPLOYEES,
            Employee.Fields.NAME
        )
        # self._validate_employee_name(name)


    def _validate_default_role(self, default_role):
        """
        We validate that the employee role is present is a valid one
        """
        if default_role is '':
            raise UserException("default_role cannot be empty.")
        elif default_role not in Employee.allowed_roles():
            raise UserException("Allowed values for default_role are %s" %
                                str(Employee.allowed_roles()))


    @authentication_handler
    @marshaling_handler
    def get(self, obj_id=None):

        if obj_id:
            employee_dict = DatabaseManager.find_document_by_id(
                Collection.EMPLOYEES, obj_id, True
            )

            return employee_dict
        else:
            query_dict = {}

            # active is an optional param, it may or may not be present. Hence
            # we explicitly check it with True or False.
            # If absent it will be None

            active = self.args.get(Params.ACTIVE, None)
            if active is True:
                query_dict[Employee.Fields.ACTIVE] = True
            elif active is False:
                query_dict[Employee.Fields.ACTIVE] = False

            default_role = self.args.get(Params.DEFAULT_ROLE, None)
            if default_role is not None:
                # It can be empty, but validate will take care of it
                self._validate_default_role(default_role)
                query_dict[Employee.Fields.DEFAULT_ROLE] = default_role

            employee_list = DatabaseManager.find(
                Collection.EMPLOYEES, query_dict, True
            )

            return employee_list


    @authentication_handler
    @marshaling_handler
    def post(self):
        """
        We always try to create an Employee object from the data posted,
        to make sure we have all the required data, if anything is absent
        an exception is raised
        """
        employee = Employee(**self.data)
        _dict = Employee.encode(employee)

        _id = DatabaseManager.insert(Collection.EMPLOYEES, _dict)
        employee_dict = DatabaseManager.find_document_by_id(
            Collection.EMPLOYEES, _id, True
        )
        return employee_dict


    @authentication_handler
    @marshaling_handler
    def patch(self, obj_id):

        query = {BaseModel.Fields._ID: obj_id}
        update = {'$set': self.data}

        result = DatabaseManager.update(
            Collection.EMPLOYEES, query, update, multi=False, upsert=False
        )
        employee_dict = DatabaseManager.find_document_by_id(
            Collection.EMPLOYEES, obj_id, True
        )
        return employee_dict

    @authentication_handler
    @delete_handler
    def delete(self, obj_id):

        result = DatabaseManager.remove(
            Collection.EMPLOYEES,
            {BaseModel.Fields._ID: obj_id},
            multiple=False
        )

        if not result['err'] and result['n']:
            return '', 204
        else:
            return '', 404