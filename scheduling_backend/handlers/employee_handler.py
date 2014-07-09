

from bson.objectid import ObjectId
from flask import current_app as current_app


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

        name = self.data.get(Employee.Fields.NAME, None)
        current_role = self.data.get(Employee.Fields.CURRENT_ROLE, None)

        self._validate_current_role(current_role)
        self.validate_name(
            name,
            Collection.EMPLOYEES,
            Employee.Fields.NAME,
            ObjectId(employee_id)
        )
        # self._validate_employee_name(name, ObjectId(employee_id))


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


    # def _validate_employee_name(self, new_employee_name, employee_id=None):
    #     """
    #     employee_id would only be present for a PATCH.
    #     It would be None in case of a POST
    #     """
    #
    #     if new_employee_name == '':
    #         raise UserException("Employee name cannot be empty")
    #
    #     matching_employee_count = DatabaseManager.find_count(
    #         Collection.EMPLOYEES,
    #         {Employee.Fields.NAME: new_employee_name}
    #     )
    #
    #     if employee_id:
    #         # This is a PATCH
    #         employee = DatabaseManager.find_object_by_id(Collection.EMPLOYEES,
    #                                                      employee_id,
    #                                                      True)
    #         if employee.name == new_employee_name:
    #             # The old employee name is being passed in a patch, let it pass
    #             pass
    #         else:
    #             # The employee name is being changed in the patch, check to make
    #             # no other employee has the same name
    #             if matching_employee_count >= 1:
    #                 # This means some other employee has same name,
    #                 #  as the new name, so we should not let
    #                 #  two employees have the same name
    #                 raise UserException("Another employee has the same name, "
    #                                     "use another name")
    #
    #     else:
    #         # This is a POST, so we only need to check if another employee has
    #         # the same name or not
    #         if matching_employee_count >= 1:
    #             raise UserException("Another employee has the same name,"
    #                                 " use another name")

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