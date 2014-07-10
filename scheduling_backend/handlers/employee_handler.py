

from bson.objectid import ObjectId

import flask.ext.restful.types

from scheduling_backend.database_manager import Collection, DatabaseManager
from scheduling_backend.exceptions import UserException
from scheduling_backend.handlers import (
    marshaling_handler, Params, delete_handler
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

        self.req_parser.add_argument(Params.CURRENT_ROLE,
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

        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)
        if current_role is not None:
            self._validate_current_role(current_role)

        name = self.data.get(Employee.Fields.NAME, None)
        self.validate_name(
            name,
            Collection.EMPLOYEES,
            Employee.Fields.NAME,
            ObjectId(employee_id)
        )


    def preprocess_POST(self):
        name = self.data.get(Employee.Fields.NAME, None)
        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)

        self._validate_current_role(current_role)
        self.validate_name(
            name,
            Collection.EMPLOYEES,
            Employee.Fields.NAME
        )
        # self._validate_employee_name(name)


    def _validate_current_role(self, current_role):
        """
        We validate that the employee role is present is a valid one
        """
        if current_role is '':
            raise UserException("current_role cannot be empty.")
        elif current_role not in Employee.allowed_roles():
            raise UserException("Allowed values for current_role are %s" %
                                str(Employee.allowed_roles()))


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

            current_role = self.args.get(Params.CURRENT_ROLE, None)
            if current_role is not None:
                # It can be empty, but validate will take care of it
                self._validate_current_role(current_role)
                query_dict[Employee.Fields.CURRENT_ROLE] = current_role

            employee_list = DatabaseManager.find(
                Collection.EMPLOYEES, query_dict, True
            )

            return employee_list


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